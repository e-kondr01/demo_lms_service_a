from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import Session
from app.models.fdwdemo import FdwDemo
from app.schemas.fdwdemo import FdwDemoSchema

router = APIRouter()


@router.get("")
async def fdwdemo(
    session: Session,
) -> list[FdwDemoSchema]:
    return (await session.execute(select(FdwDemo))).scalars().all()
