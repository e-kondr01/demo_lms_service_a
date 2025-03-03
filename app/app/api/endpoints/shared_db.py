from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from app.api.deps import Session
from app.managers.assessment import assessment_manager
from app.schemas import AssessmentSchema

router = APIRouter()


@router.get("")
async def get_assessments_shared(
    session: Session,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
    unit_name: str | None = None,
    assessment_grade: int | None = None,
) -> Page[AssessmentSchema]:
    return await assessment_manager.get_list_shared_db(
        session,
        unit_id=unit_id,
        institution_id=institution_id,
        unit_name=unit_name,
        assessment_grade=assessment_grade,
    )  # type: ignore
