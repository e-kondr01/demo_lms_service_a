from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.institution import Institution

from app.models import Base


class Student(Base):
    name: Mapped[str] = mapped_column(String(63))

    institution_id: Mapped[UUID] = mapped_column(ForeignKey("institution.id"))
    institution: Mapped["Institution"] = relationship()
