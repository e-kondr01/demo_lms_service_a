from fastapi_sqlalchemy_toolkit import ModelManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models import Student, StudentProgress, Unit
from app.schemas import StudentProgressSchema


class StudentProgressManager(
    ModelManager[StudentProgress, StudentProgressSchema, StudentProgressSchema]
):
    async def get_list_cqrs(
        self,
        session: AsyncSession,
        unit_name_q: str | None = None,
        student_name_q: str | None = None,
    ) -> list[StudentProgress]:
        stmt = (
            select(StudentProgress)
            .join(StudentProgress.student)
            .join(StudentProgress.current_unit)
            .options(
                contains_eager(StudentProgress.current_unit),
                contains_eager(StudentProgress.student),
            )
        )

        if unit_name_q:
            stmt = stmt.filter(Unit.name.icontains(f"%{unit_name_q}%"))

        if student_name_q:
            stmt = stmt.filter(Student.name.icontains(f"%{student_name_q}%"))

        return (await session.execute(stmt)).scalars().all()


student_progress_manager = StudentProgressManager(StudentProgress)
