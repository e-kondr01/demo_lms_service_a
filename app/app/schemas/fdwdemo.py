from uuid import UUID

from pydantic import BaseModel


class FdwDemoSchema(BaseModel):
    id: UUID
    name: str
