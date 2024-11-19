from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class ServiceBInstitution(Base):
    name: Mapped[str] = mapped_column(String(255))


class ServiceBStudent(Base):
    name: Mapped[str] = mapped_column(String(63))

    institution_id: Mapped[UUID] = mapped_column(
        ForeignKey("servicebinstitution.id"), index=True
    )
    institution: Mapped["ServiceBInstitution"] = relationship()


class ServiceCUnit(Base):
    name: Mapped[str] = mapped_column(String(255))
