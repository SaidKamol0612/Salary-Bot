from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models

from .role import RoleCRUD


class ShiftRoleCRUD:
    @staticmethod
    async def add_shift_roles_by_name(
        session: AsyncSession, shift_id: int, roles: list[str]
    ) -> None:
        shift_roles = []
        for role_name in roles:
            print(roles)
            role = await RoleCRUD.get_role_by_name(session, role_name)
            if role is None:
                raise ValueError(f"❌ Role not found: {role_name}")
            shift_roles.append(models.ShiftRole(shift_id=shift_id, role_id=role.id))

        session.add_all(shift_roles)

    @staticmethod
    async def get_shift_roles(
        session: AsyncSession, shift_id: int
    ) -> list[models.ShiftRole]:
        stmt = select(models.ShiftRole).where(models.ShiftRole.shift_id == shift_id)
        res = await session.scalars(stmt)
        return res.all()
