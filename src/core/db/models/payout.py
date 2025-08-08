from typing import TYPE_CHECKING
from datetime import date

from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Payout(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(nullable=False)
    paid_at: Mapped[date] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    note: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="payouts")
