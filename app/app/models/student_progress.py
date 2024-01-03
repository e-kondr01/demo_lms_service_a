from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.unit import Unit


class StudentProgress(Base):
    current_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("unit.id"),
        comment="id элемента курса, на котором остановился студент",
    )
    current_unit: Mapped["Unit"] = relationship()

    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("student.id"), unique=True, index=True
    )
    student: Mapped["Student"] = relationship()
