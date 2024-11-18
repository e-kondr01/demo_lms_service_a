from asyncio import TaskGroup
from datetime import datetime
from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_sqlalchemy_toolkit import ModelManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models import (
    Assessment,
    AssessmentFDWThreeServices,
    AssessmentFDWTwoServices,
    Student,
    Unit,
)
from app.models.institution import ForeignInstitution
from app.models.student import ForeignStudent
from app.models.unit import ForeignUnit
from app.schemas import AssessmentSchema
from app.services.service_b import service_b
from app.services.service_c import service_c


def two_services_fdw_row_to_assessment(rows) -> list[AssessmentFDWTwoServices]:
    formatted_rows = []
    for row in rows:
        row.ForeignStudent.institution = row.ForeignInstitution
        row.AssessmentFDWTwoServices.student = row.ForeignStudent
        formatted_rows.append(row.AssessmentFDWTwoServices)
    return formatted_rows


def three_services_fdw_row_to_assessment(rows) -> list[AssessmentFDWThreeServices]:
    formatted_rows = []
    for row in rows:
        row.ForeignStudent.institution = row.ForeignInstitution
        row.AssessmentFDWThreeServices.student = row.ForeignStudent
        row.AssessmentFDWThreeServices.unit = row.ForeignUnit
        formatted_rows.append(row.AssessmentFDWThreeServices)
    return formatted_rows


class AssessmentManager(ModelManager[Assessment, AssessmentSchema, AssessmentSchema]):
    async def get_list_shared_db(
        self,
        session: AsyncSession,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> Page[Assessment]:
        stmt = (
            select(Assessment)
            .join(Assessment.student)
            .join(Assessment.unit)
            .options(
                contains_eager(Assessment.unit),
                contains_eager(Assessment.student).joinedload(Student.institution),
            )
            .order_by(Assessment.created_at)
        )

        if unit_id:
            stmt = stmt.filter(Unit.id == unit_id)

        if institution_id:
            stmt = stmt.filter(Student.institution_id == institution_id)

        return await paginate(session, stmt)

    async def get_list_fdw_two_services(
        self,
        session: AsyncSession,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> Page[AssessmentFDWTwoServices]:
        stmt = (
            select(AssessmentFDWTwoServices, ForeignStudent, ForeignInstitution)
            .join_from(
                AssessmentFDWTwoServices,
                ForeignStudent,
                AssessmentFDWTwoServices.student_id == ForeignStudent.id,
            )
            .join_from(
                ForeignStudent,
                ForeignInstitution,
                ForeignStudent.institution_id == ForeignInstitution.id,
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
            stmt = stmt.filter(ForeignStudent.institution_id == institution_id)

        return await paginate(
            session, stmt, transformer=two_services_fdw_row_to_assessment
        )

    async def get_list_fdw_three_services(
        self,
        session: AsyncSession,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> Page[AssessmentFDWThreeServices]:
        stmt = (
            select(
                AssessmentFDWThreeServices,
                ForeignStudent,
                ForeignInstitution,
                ForeignUnit,
            )
            .join_from(
                AssessmentFDWThreeServices,
                ForeignUnit,
                AssessmentFDWThreeServices.unit_id == ForeignUnit.id,
            )
            .join(
                ForeignStudent,
                AssessmentFDWThreeServices.student_id == ForeignStudent.id,
            )
            .join(
                ForeignInstitution,
                ForeignStudent.institution_id == ForeignInstitution.id,
            )
            .order_by(AssessmentFDWThreeServices.created_at)
        )

        if unit_id:
            stmt = stmt.filter(ForeignUnit.id == unit_id)

        if institution_id:
            stmt = stmt.filter(ForeignStudent.institution_id == institution_id)

        return await paginate(
            session, stmt, transformer=three_services_fdw_row_to_assessment
        )

    async def get_list_cyclic_api_composition_two_services(
        self,
        session: AsyncSession,
        page_size: int = 20,
        previous_created_at: datetime | None = None,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> list[AssessmentSchema]:
        filtered_result: list[AssessmentSchema] = []

        base_stmt = (
            select(Assessment)
            .join(Assessment.unit)
            .options(
                contains_eager(Assessment.unit),
            )
            .order_by(Assessment.created_at)
            .limit(page_size)
        )
        if unit_id:
            base_stmt = base_stmt.filter(Unit.id == unit_id)
        if previous_created_at:
            base_stmt = base_stmt.filter(Assessment.created_at > previous_created_at)

        offset = 0
        while True:
            stmt = base_stmt.offset(offset)
            assessments = (await session.execute(stmt)).scalars().all()
            if not assessments:
                return filtered_result
            student_ids = {str(assessment.student_id) for assessment in assessments}
            students_by_id = await service_b.get_students(
                student_ids,
                institution_id=institution_id,
                limit=page_size - len(filtered_result),
            )
            for assessment in assessments:
                if assessment.student_id in students_by_id:
                    filtered_result.append(
                        AssessmentSchema(
                            unit=assessment.unit,
                            grade=assessment.grade,
                            student=students_by_id[assessment.student_id],
                            created_at=assessment.created_at,
                        )
                    )
                    if len(filtered_result) == page_size:
                        return filtered_result
            offset += page_size

    async def get_prefilter_list_api_composition_two_services(
        self,
        session: AsyncSession,
        page_size: int = 20,
        page_number: int = 1,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> list[AssessmentSchema]:
        if institution_id:
            student_id_stmt = select(Assessment.student_id)
            if unit_id:
                student_id_stmt = student_id_stmt.where(Assessment.unit_id == unit_id)
            student_ids = (await session.execute(student_id_stmt)).scalars().all()
            filtered_student_ids = await service_b.get_student_ids(
                {str(student_id) for student_id in student_ids},
                institution_id=institution_id,
            )

        stmt = (
            select(Assessment)
            .join(Assessment.unit)
            .options(
                contains_eager(Assessment.unit),
            )
            .order_by(Assessment.created_at)
            .limit(page_size)
            .offset(page_size * (page_number - 1))
        )
        if institution_id:
            stmt = stmt.where(Assessment.student_id.in_(filtered_student_ids))
        if unit_id:
            stmt = stmt.where(Assessment.unit_id == unit_id)
        assessments = (await session.execute(stmt)).scalars().all()
        if not assessments:
            return []
        result_student_ids = {str(assessment.student_id) for assessment in assessments}
        students_by_id = await service_b.get_students(
            result_student_ids,
        )

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

    async def get_list_cyclic_api_composition_three_services(
        self,
        session: AsyncSession,
        page_size: int = 20,
        previous_created_at: datetime | None = None,
        institution_id: UUID | None = None,
        unit_name: str | None = None,
    ) -> list[AssessmentSchema]:
        filtered_result: list[AssessmentSchema] = []

        base_stmt = select(Assessment).order_by(Assessment.created_at).limit(page_size)
        if previous_created_at:
            base_stmt = base_stmt.filter(Assessment.created_at > previous_created_at)

        offset = 0
        while True:
            stmt = base_stmt.offset(offset)
            assessments = (await session.execute(stmt)).scalars().all()
            if not assessments:
                return filtered_result

            student_ids = set()
            for assessment in assessments:
                student_ids.add(str(assessment.student_id))

            students_by_id = await service_b.get_students(
                student_ids,
                institution_id=institution_id,
                limit=page_size - len(filtered_result),
            )

            unit_ids = set()
            for assessment in assessments:
                if assessment.student_id in students_by_id:
                    unit_ids.add(str(assessment.unit_id))
            units_by_id = await service_c.get_units(
                unit_ids,
                name=unit_name,
                limit=page_size - len(filtered_result),
            )

            for assessment in assessments:
                if assessment.student_id in students_by_id and units_by_id:
                    filtered_result.append(
                        AssessmentSchema(
                            unit=units_by_id[assessment.unit_id],
                            grade=assessment.grade,
                            student=students_by_id[assessment.student_id],
                            created_at=assessment.created_at,
                        )
                    )
                    if len(filtered_result) == page_size:
                        return filtered_result
            offset += page_size

    async def get_prefilter_list_api_composition_three_services(
        self,
        session: AsyncSession,
        page_size: int = 20,
        page_number: int = 1,
        unit_name: str | None = None,
        institution_id: UUID | None = None,
    ) -> list[AssessmentSchema]:
        if institution_id:
            student_id_stmt = select(Assessment.student_id)
            student_ids = (await session.execute(student_id_stmt)).scalars().all()

            filtered_student_ids = await service_b.get_student_ids(
                {str(student_id) for student_id in student_ids},
                institution_id=institution_id,
            )

        if unit_name:
            unit_id_stmt = select(Assessment.unit_id).where(
                Assessment.student_id.in_(filtered_student_ids)
            )
            unit_ids = (await session.execute(unit_id_stmt)).scalars().all()
            filtered_unit_ids = await service_c.get_unit_ids(
                {str(unit_id) for unit_id in unit_ids},
                unit_name=unit_name,
            )

        stmt = (
            select(Assessment)
            .order_by(Assessment.created_at)
            .limit(page_size)
            .offset(page_size * (page_number - 1))
        )
        if institution_id:
            stmt = stmt.where(Assessment.student_id.in_(filtered_student_ids))
        if unit_name:
            stmt = stmt.where(Assessment.unit_id.in_(filtered_unit_ids))

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
