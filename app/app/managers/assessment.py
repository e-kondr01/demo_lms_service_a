from asyncio import TaskGroup
from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_sqlalchemy_toolkit import ModelManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from app.models import (
    Assessment,
    AssessmentFDWThreeServices,
    AssessmentFDWTwoServices,
    Student,
    Unit,
)
from app.models.foreign import ServiceBInstitution, ServiceBStudent, ServiceCUnit
from app.schemas import AssessmentSchema
from app.services.service_b import service_b
from app.services.service_c import service_c


def two_services_fdw_row_to_assessment(rows) -> list[AssessmentFDWTwoServices]:
    formatted_rows = []
    for row in rows:
        row.ServiceBStudent.institution = row.ServiceBInstitution
        row.AssessmentFDWTwoServices.student = row.ServiceBStudent
        formatted_rows.append(row.AssessmentFDWTwoServices)
    return formatted_rows


def three_services_fdw_row_to_assessment(rows) -> list[AssessmentFDWThreeServices]:
    formatted_rows = []
    for row in rows:
        row.ServiceBStudent.institution = row.ServiceBInstitution
        row.AssessmentFDWThreeServices.student = row.ServiceBStudent
        row.AssessmentFDWThreeServices.unit = row.ServiceCUnit
        formatted_rows.append(row.AssessmentFDWThreeServices)
    return formatted_rows


class AssessmentManager(ModelManager[Assessment, AssessmentSchema, AssessmentSchema]):
    async def get_list_shared_db(
        self,
        session: AsyncSession,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
        unit_name: str | None = None,
        assessment_grade: int | None = None,
    ) -> Page[Assessment]:
        stmt = (
            select(Assessment)
            .options(
                joinedload(Assessment.unit),
                joinedload(Assessment.student).joinedload(Student.institution),
            )
            .order_by(Assessment.created_at)
        )

        if unit_id:
            stmt = stmt.filter(Assessment.unit_id == unit_id)

        if unit_name:
            stmt = stmt.join(Assessment.unit).where(Unit.name == unit_name)

        if institution_id:
            stmt = stmt.join(Assessment.student).filter(
                Student.institution_id == institution_id
            )

        if assessment_grade:
            stmt = stmt.where(Assessment.grade == assessment_grade)

        return await paginate(session, stmt)

    async def get_list_fdw_two_services(
        self,
        session: AsyncSession,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> Page[AssessmentFDWTwoServices]:
        stmt = (
            select(AssessmentFDWTwoServices, ServiceBStudent, ServiceBInstitution)
            .join_from(
                AssessmentFDWTwoServices,
                ServiceBStudent,
                AssessmentFDWTwoServices.student_id == ServiceBStudent.id,
            )
            .join_from(
                ServiceBStudent,
                ServiceBInstitution,
                ServiceBStudent.institution_id == ServiceBInstitution.id,
            )
            .join(AssessmentFDWTwoServices.unit)
            .options(
                contains_eager(AssessmentFDWTwoServices.unit),
            )
            .order_by(AssessmentFDWTwoServices.created_at)
        )

        if unit_id:
            stmt = stmt.filter(Unit.id == unit_id)

        if institution_id:
            stmt = stmt.filter(ServiceBStudent.institution_id == institution_id)

        return await paginate(
            session, stmt, transformer=two_services_fdw_row_to_assessment
        )

    async def get_list_fdw_three_services(
        self,
        session: AsyncSession,
        unit_name: str | None = None,
        institution_id: UUID | None = None,
        assessment_grade: int | None = None,
    ) -> Page[AssessmentFDWThreeServices]:
        stmt = (
            select(
                AssessmentFDWThreeServices,
                ServiceBStudent,
                ServiceBInstitution,
                ServiceCUnit,
            )
            .join_from(
                AssessmentFDWThreeServices,
                ServiceCUnit,
                AssessmentFDWThreeServices.unit_id == ServiceCUnit.id,
            )
            .join(
                ServiceBStudent,
                AssessmentFDWThreeServices.student_id == ServiceBStudent.id,
            )
            .join(
                ServiceBInstitution,
                ServiceBStudent.institution_id == ServiceBInstitution.id,
            )
            .order_by(AssessmentFDWThreeServices.created_at)
        )

        if unit_name:
            stmt = stmt.filter(ServiceCUnit.name == unit_name)

        if institution_id:
            stmt = stmt.filter(ServiceBStudent.institution_id == institution_id)

        if assessment_grade:
            stmt = stmt.filter(AssessmentFDWThreeServices.grade == assessment_grade)

        return await paginate(
            session, stmt, transformer=three_services_fdw_row_to_assessment
        )

    async def get_list_api_composition_two_services(
        self,
        session: AsyncSession,
        page_size: int = 20,
        page_number: int = 1,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> list[AssessmentSchema]:
        if institution_id:
            student_id_stmt = select(AssessmentFDWTwoServices.student_id).distinct()
            if unit_id:
                student_id_stmt = student_id_stmt.where(
                    AssessmentFDWTwoServices.unit_id == unit_id
                )
            student_ids = (await session.execute(student_id_stmt)).scalars()
            if not student_ids:
                return []

            filtered_student_ids = await service_b.get_student_ids(
                {str(student_id) for student_id in student_ids},
                institution_id=institution_id,
            )
            if not filtered_student_ids:
                return []

        stmt = (
            select(AssessmentFDWTwoServices)
            .join(AssessmentFDWTwoServices.unit)
            .options(
                contains_eager(AssessmentFDWTwoServices.unit),
            )
            .order_by(AssessmentFDWTwoServices.created_at)
            .limit(page_size)
            .offset(page_size * (page_number - 1))
        )
        if institution_id:
            stmt = stmt.where(
                AssessmentFDWTwoServices.student_id.in_(filtered_student_ids)
            )
        if unit_id:
            stmt = stmt.where(AssessmentFDWTwoServices.unit_id == unit_id)
        assessments = (await session.execute(stmt)).scalars().all()
        if not assessments:
            return []
        result_student_ids = {str(assessment.student_id) for assessment in assessments}
        students_by_id = await service_b.get_students(result_student_ids)

        result = []
        for assessment in assessments:
            result.append(
                AssessmentSchema(
                    unit=assessment.unit,
                    grade=assessment.grade,
                    student=students_by_id[assessment.student_id],
                    created_at=assessment.created_at,
                )
            )
        return result

    async def get_list_api_composition_three_services(
        self,
        session: AsyncSession,
        page_size: int = 20,
        page_number: int = 1,
        unit_name: str | None = None,
        institution_id: UUID | None = None,
        assessment_grade: int | None = None,
    ) -> list[AssessmentSchema]:
        if institution_id:
            student_id_stmt = select(AssessmentFDWThreeServices.student_id).distinct()
            if assessment_grade:
                student_id_stmt = student_id_stmt.filter(
                    AssessmentFDWThreeServices.grade == assessment_grade
                )
            student_ids = (await session.execute(student_id_stmt)).scalars()
            if not student_ids:
                return []

            filtered_student_ids = await service_b.get_student_ids(
                {str(student_id) for student_id in student_ids},
                institution_id=institution_id,
            )
            if not filtered_student_ids:
                return []

        if unit_name:
            unit_id_stmt = select(AssessmentFDWThreeServices.unit_id).distinct()

            if institution_id:
                unit_id_stmt = unit_id_stmt.where(
                    AssessmentFDWThreeServices.student_id.in_(filtered_student_ids)
                )

            if assessment_grade:
                unit_id_stmt = unit_id_stmt.filter(
                    AssessmentFDWThreeServices.grade == assessment_grade
                )
            unit_ids = (await session.execute(unit_id_stmt)).scalars()
            if not unit_ids:
                return []

            filtered_unit_ids = await service_c.get_unit_ids(
                {str(unit_id) for unit_id in unit_ids},
                name=unit_name,
            )
            if not filtered_unit_ids:
                return []

        stmt = (
            select(AssessmentFDWThreeServices)
            .order_by(AssessmentFDWThreeServices.created_at)
            .limit(page_size)
            .offset(page_size * (page_number - 1))
        )
        if institution_id:
            stmt = stmt.where(
                AssessmentFDWThreeServices.student_id.in_(filtered_student_ids)
            )
        if unit_name:
            stmt = stmt.where(AssessmentFDWThreeServices.unit_id.in_(filtered_unit_ids))
        if assessment_grade:
            stmt = stmt.filter(AssessmentFDWThreeServices.grade == assessment_grade)

        assessments = (await session.execute(stmt)).scalars().all()
        if not assessments:
            return []

        async with TaskGroup() as tg:
            result_student_ids = {
                str(assessment.student_id) for assessment in assessments
            }
            students_task = tg.create_task(
                service_b.get_students(
                    result_student_ids,
                )
            )

            result_unit_ids = {str(assessment.unit_id) for assessment in assessments}
            units_task = tg.create_task(
                service_c.get_units(
                    result_unit_ids,
                )
            )
        students_by_id = students_task.result()
        units_by_id = units_task.result()

        result = []
        for assessment in assessments:
            result.append(
                AssessmentSchema(
                    unit=units_by_id[assessment.unit_id],
                    grade=assessment.grade,
                    student=students_by_id[assessment.student_id],
                    created_at=assessment.created_at,
                )
            )
        return result


assessment_manager = AssessmentManager(Assessment)
