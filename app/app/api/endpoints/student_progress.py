from fastapi import APIRouter

from app.deps import Session
from app.managers.student_progress import student_progress_manager
from app.schemas import StudentProgressSchema

router = APIRouter()


@router.get("")
async def get_student_progresses(
    session: Session, student_name: str | None = None, unit_name: str | None = None
) -> list[StudentProgressSchema]:
    return await student_progress_manager.get_list_cqrs(
        session, student_name_q=student_name, unit_name_q=unit_name
    )
