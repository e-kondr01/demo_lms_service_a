from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from app.api.deps import Session
from app.managers.assessment import assessment_manager
from app.schemas import AssessmentSchema

router = APIRouter()


@router.get("/cqrs")
async def get_assessments_cqrs(
    session: Session,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> Page[AssessmentSchema]:
    return await assessment_manager.get_list_cqrs(
        session, unit_id=unit_id, institution_id=institution_id
    )  # type: ignore


@router.get("/cyclic-api-composition")
async def get_assessments_cyclic(
    session: Session,
    page_size: int = 20,
    previous_created_at: datetime | None = None,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_list_cyclic_api_composition(
        session,
        page_size=page_size,
        previous_created_at=previous_created_at,
        unit_id=unit_id,
        institution_id=institution_id,
    )


@router.get("/paginated-api-composition")
async def get_paginated_assessments_api_composition(
    session: Session,
    page_size: int = 20,
    page_number: int = 1,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> list[AssessmentSchema]:
    return await assessment_manager.get_paginated_list_api_composition(
        session,
        page_size=page_size,
        page_number=page_number,
        unit_id=unit_id,
        institution_id=institution_id,
    )
