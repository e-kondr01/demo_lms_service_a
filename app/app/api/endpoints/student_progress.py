from fastapi import APIRouter

from app.deps import Session
from app.managers.student_progress import student_progress_manager
from app.schemas.student_progress import StudentProgressSchema

router = APIRouter()


@router.get("")
async def get_student_progresses(session: Session) -> list[StudentProgressSchema]:
    return await student_progress_manager.list(session)
