from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.unit import Unit


class Assessment(Base):
    unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("unit.id"),
    )
    unit: Mapped["Unit"] = relationship()

    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("student.id"), unique=True, index=True
    )
    student: Mapped["Student"] = relationship()

    grade: Mapped[int | None]

    __table_args__ = (
        CheckConstraint(
            "grade >= 0 and grade <= 100",
            name="grade_range",
        ),
    )
