from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.unit import Unit


class Assessment(Base):
    unit_id: Mapped[UUID] = mapped_column(ForeignKey("unit.id"), index=True)
    unit: Mapped["Unit"] = relationship()

    student_id: Mapped[UUID] = mapped_column(ForeignKey("student.id"), index=True)
    student: Mapped["Student"] = relationship()

    grade: Mapped[int | None]

    __table_args__ = (
        CheckConstraint(
            "grade >= 0 and grade <= 100",
            name="grade_range",
        ),
        UniqueConstraint(
            "student_id", "unit_id", name="unique_assessment_for_student_and_unit"
        ),
    )


class AssessmentFDWTwoServices(Base):
    unit_id: Mapped[UUID] = mapped_column(ForeignKey("unit.id"), index=True)
    unit: Mapped["Unit"] = relationship()

    student_id: Mapped[UUID] = mapped_column(index=True)

    grade: Mapped[int | None]

    __table_args__ = (
        CheckConstraint(
            "grade >= 0 and grade <= 100",
            name="grade_range",
        ),
        UniqueConstraint(
            "student_id",
            "unit_id",
            name="unique_assessment_two_fdw_for_student_and_unit",
        ),
    )


class AssessmentFDWThreeServices(Base):
    unit_id: Mapped[UUID] = mapped_column(index=True)

    student_id: Mapped[UUID] = mapped_column(index=True)

    grade: Mapped[int | None]

    __table_args__ = (
        CheckConstraint(
            "grade >= 0 and grade <= 100",
            name="grade_range",
        ),
        UniqueConstraint(
            "student_id",
            "unit_id",
            name="unique_assessment_three_fdw_for_student_and_unit",
        ),
    )
