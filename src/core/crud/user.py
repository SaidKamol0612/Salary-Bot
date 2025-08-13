from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models
from core.config import settings


class UserCRUD:
    @staticmethod
    async def get_user_by_name(session: AsyncSession, name: str) -> models.User | None:
        stmt = select(models.User).where(models.User.name == name)
        return await session.scalar(stmt)

    @staticmethod
    async def get_user_by_tg_id(
        session: AsyncSession, tg_id: int
    ) -> models.User | None:
        stmt = select(models.User).where(models.User.tg_id == tg_id)
        return await session.scalar(stmt)

    @staticmethod
    async def add_user(session: AsyncSession, tg_id: int, name: str) -> None:
        new_user = models.User(
            tg_id=tg_id, name=name, is_admin=tg_id in settings.admin.admin_ids
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

    @staticmethod
    async def get_workers_names(session: AsyncSession) -> list[models.User]:
        stmt = select(models.User.name).where(models.User.is_admin.is_(False))
        res = await session.scalars(stmt)
        return res.all()
