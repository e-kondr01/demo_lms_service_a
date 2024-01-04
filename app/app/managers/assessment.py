from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_sqlalchemy_toolkit import ModelManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models import Assessment, Student, Unit
from app.schemas import AssessmentSchema


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


assessment_manager = AssessmentManager(Assessment)
