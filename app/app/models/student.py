from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.institution import Institution


class Student(Base):
    name: Mapped[str] = mapped_column(String(63))

    institution_id: Mapped[UUID] = mapped_column(
        ForeignKey("institution.id"), index=True
    )
    institution: Mapped["Institution"] = relationship()
