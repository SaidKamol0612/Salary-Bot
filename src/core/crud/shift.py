from datetime import date as py_date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models

from .user import UserCRUD
from .shift_role import ShiftRoleCRUD


class ShiftCRUD:
    @staticmethod
    async def add_shifts(
        session: AsyncSession, date: py_date, records_data: list[dict]
    ) -> None:
        for data in records_data:
            user = await UserCRUD.get_user_by_name(session, data.get("name"))
            if user is None:
                raise ValueError(f"❌ User not found: {data.get('name')}")

            shift = models.Shift(
                user_id=user.id,
                date=date,
                start_time=data["start_time"],
                end_time=data["end_time"],
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
