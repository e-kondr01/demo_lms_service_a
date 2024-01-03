from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session: AsyncSession = async_session_factory()  # type: ignore
    try:
        yield async_session
    finally:
        await async_session.close()


Session = Annotated[AsyncSession, Depends(get_async_session)]
