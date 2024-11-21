from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from app.api.deps import Session
from app.managers.assessment import assessment_manager
from app.schemas import AssessmentSchema

router = APIRouter()


@router.get("/two-services")
async def get_assessments_fdw_two_services(
    session: Session,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> Page[AssessmentSchema]:
    return await assessment_manager.get_list_fdw_two_services(
        session, unit_id=unit_id, institution_id=institution_id
    )  # type: ignore


@router.get("/three-services")
async def get_assessments_fdw_three_services(
    session: Session,
    unit_name: str | None = None,
    institution_id: UUID | None = None,
    assessment_grade: int | None = None,
) -> Page[AssessmentSchema]:
    return await assessment_manager.get_list_fdw_three_services(
        session,
        unit_name=unit_name,
        institution_id=institution_id,
        assessment_grade=assessment_grade,
    )  # type: ignore
