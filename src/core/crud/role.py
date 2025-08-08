from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models
from core.enums import Role as RoleEnum


class RoleCRUD:
    @staticmethod
    async def get_role_by_name(session: AsyncSession, name: str) -> models.Role | None:
        stmt = select(models.Role).where(models.Role.name == name)
        return await session.scalar(stmt)

    @staticmethod
    async def get_role_by_id(session: AsyncSession, role_id: int) -> models.Role | None:
        stmt = select(models.Role).where(models.Role.id == role_id)
        return await session.scalar(stmt)

    @staticmethod
    async def exists(session: AsyncSession):
        stmt = select(models.Role).limit(1)
        res = await session.scalar(stmt)

        return res

    @staticmethod
    async def set_roles(session: AsyncSession, day_rates: list, night_rates: list):
        for i, r in enumerate(RoleEnum):
            role = models.Role(
                code=r,
                name=r.name,
                rate_day=day_rates[i],
                rate_night=night_rates[i],
            )

            session.add(role)
        await session.commit()
