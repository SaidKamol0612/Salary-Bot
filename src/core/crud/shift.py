from datetime import date as py_date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models

from .user import UserCRUD
from .shift_role import ShiftRoleCRUD


class ShiftCRUD:
    @staticmethod
    async def add_shift(session: AsyncSession, date: py_date, data: dict) -> None:
        user = await UserCRUD.get_user_by_name(session, data.get("name"))
        if user is None:
            raise ValueError(f"❌ User not found: {data.get('name')}")

        shift = models.Shift(
            user_id=user.id,
            date=date,
            count_dough=data.get("count_dough", 0),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            shift_type=data["shift_type"],
            bonus=data.get("bonus", 0),
        )
        session.add(shift)
        await session.flush()

        await ShiftRoleCRUD.add_shift_roles_by_name(
            session, shift.id, data.get("roles", [])
        )

        await session.commit()

    @staticmethod
    async def get_shifts(session: AsyncSession, user_id: int) -> list[models.Shift]:
        stmt = select(models.Shift).where(models.Shift.user_id == user_id)
        res = await session.scalars(stmt)
        return res.all()
