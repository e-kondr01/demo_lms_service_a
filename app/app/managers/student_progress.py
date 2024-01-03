from fastapi_sqlalchemy_toolkit import ModelManager

from app.models import StudentProgress
from app.schemas.student_progress import StudentProgressSchema


class StudentProgressManager(
    ModelManager[StudentProgress, StudentProgressSchema, StudentProgressSchema]
):
    pass


student_progress_manager = StudentProgressManager(StudentProgress)
