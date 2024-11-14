from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from app.api.deps import Session
from app.managers.assessment import assessment_manager
from app.schemas import AssessmentSchema

router = APIRouter()


@router.get("/shared")
async def get_assessments_shared(
    session: Session,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> Page[AssessmentSchema]:
    return await assessment_manager.get_list_shared_db(
        session, unit_id=unit_id, institution_id=institution_id
    )  # type: ignore


@router.get("/two-services-cyclic-api-composition")
async def get_assessments_cyclic(
    session: Session,
    size: int = 20,
    previous_created_at: datetime | None = None,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_list_cyclic_api_composition_two_services(
        session,
        page_size=size,
        previous_created_at=previous_created_at,
        unit_id=unit_id,
        institution_id=institution_id,
    )


@router.get("/two-services-prefilter-api-composition")
async def get_paginated_assessments_api_composition(
    session: Session,
    size: int = 20,
    page: int = 1,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_prefilter_list_api_composition_two_services(
        session,
        page_size=size,
        page_number=page,
        unit_id=unit_id,
        institution_id=institution_id,
    )


@router.get("/three-services-cyclic-api-composition")
async def get_assessments_cyclic_three_services(
    session: Session,
    size: int = 20,
    previous_created_at: datetime | None = None,
    institution_id: UUID | None = None,
    unit_name: str | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_list_cyclic_api_composition_three_services(
        session,
        page_size=size,
        previous_created_at=previous_created_at,
        institution_id=institution_id,
        unit_name=unit_name,
    )


@router.get("/three-services-prefilter-api-composition")
async def get_paginated_assessments_api_composition_three_services(
    session: Session,
    size: int = 20,
    page: int = 1,
    institution_id: UUID | None = None,
    unit_name: str | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_prefilter_list_api_composition_three_services(
        session,
        page_size=size,
        page_number=page,
        institution_id=institution_id,
        unit_name=unit_name,
    )
