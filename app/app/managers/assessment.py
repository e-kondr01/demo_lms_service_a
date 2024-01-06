from datetime import datetime
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
            students = await service_b.get_students(
                student_ids,
                institution_id=institution_id,
                limit=page_size - len(filtered_result),
            )
            students_by_id = {student.id: student for student in students}
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

    async def get_paginated_list_api_composition(
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
        students = await service_b.get_students(
            result_student_ids,
        )
        students_by_id = {student.id: student for student in students}
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


assessment_manager = AssessmentManager(Assessment)
