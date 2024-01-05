from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_sqlalchemy_toolkit import ModelManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models import Assessment, Student, Unit
from app.schemas import AssessmentSchema
from app.services.service_b import service_b


class AssessmentManager(ModelManager[Assessment, AssessmentSchema, AssessmentSchema]):
    async def get_list_cqrs(
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

    async def get_list_cyclic_api_composition(
        self,
        session: AsyncSession,
        page_size: int = 20,
        page_number: int = 1,
        unit_id: UUID | None = None,
        institution_id: UUID | None = None,
    ) -> list[AssessmentSchema]:
        # TODO: неправильно отдаёт результаты последующих страниц,
        # если на предыдущих были пропуски от второго сервиса
        filtered_result: list[AssessmentSchema] = []
        offset = page_size * (page_number - 1)

        while True:
            stmt = (
                select(Assessment)
                .join(Assessment.unit)
                .options(
                    contains_eager(Assessment.unit),
                )
                .order_by(Assessment.created_at)
                .limit(page_size)
                .offset(offset)
            )
            if unit_id:
                stmt = stmt.filter(Unit.id == unit_id)
            assessments = (await session.execute(stmt)).scalars().all()
            if not assessments:
                return filtered_result
            student_ids = {str(assessment.student_id) for assessment in assessments}
            students = await service_b.get_students(
                student_ids, institution_id=institution_id
            )
            assessments_by_student_id = {
                assessment.student_id: assessment for assessment in assessments
            }
            for student in students:
                if student.id in assessments_by_student_id:
                    filtered_result.append(
                        AssessmentSchema(
                            unit=assessments_by_student_id[student.id].unit,
                            grade=assessments_by_student_id[student.id].grade,
                            student=student,
                        )
                    )
                    if len(filtered_result) == page_size:
                        return filtered_result
            offset += page_size


assessment_manager = AssessmentManager(Assessment)
