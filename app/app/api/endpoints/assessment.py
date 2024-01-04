from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from app.api.deps import Session
from app.managers.assessment import assessment_manager
from app.schemas import AssessmentSchema
from app.services.service_b import service_b

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


# TODO: наивный API composition с получением в цикле
@router.get("/cyclic-api-composition")
async def get_assessments_cyclic(
    session: Session,
    unit_id: UUID | None = None,
    institution_id: UUID | None = None,
) -> Page[AssessmentSchema]:
    students = await service_b.get_students(
        {
            "fe9e186e-26d1-4046-a557-70b3e805c256",
            "ec7c8d13-aae5-43e0-99b2-a47cbb02c4cc",
        }
    )
    return await assessment_manager.get_list_cqrs(
        session, unit_id=unit_id, institution_id=institution_id
    )  # type: ignore


# TODO: API composition через select id where
