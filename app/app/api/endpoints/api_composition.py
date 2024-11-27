from uuid import UUID

from fastapi import APIRouter

from app.api.deps import Session
from app.managers.assessment import assessment_manager
from app.schemas import AssessmentSchema

router = APIRouter()


@router.get("/two-services")
async def get_assessments_api_composition(
    session: Session,
    size: int = 20,
    page: int = 1,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_list_api_composition_two_services(
        session,
        page_size=size,
        page_number=page,
        unit_id=unit_id,
        institution_id=institution_id,
    )


@router.get("/three-services")
async def get_assessments_api_composition_three_services(
    session: Session,
    size: int = 20,
    page: int = 1,
    institution_id: UUID | None = None,
    unit_name: str | None = None,
    assessment_grade: int | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_list_api_composition_three_services(
        session,
        page_size=size,
        page_number=page,
        institution_id=institution_id,
        unit_name=unit_name,
        assessment_grade=assessment_grade,
    )
