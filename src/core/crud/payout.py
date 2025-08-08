from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models


class PayoutCRUD:
    @staticmethod
    async def get_payouts(session: AsyncSession, user_id: int) -> list[models.Payout]:
        stmt = select(models.Payout).where(models.Payout.user_id == user_id)
        res = await session.scalars(stmt)
        return [p for p in res.all()]

    @staticmethod
    async def add_payout(
        session: AsyncSession, user_id: int, amount: int, paid_at: datetime, note: str
    ):
        new_payout = models.Payout(
            user_id=user_id, amount=amount, paid_at=paid_at, note=note
        )
        session.add(new_payout)
        await session.commit()
        await session.refresh(new_payout)
