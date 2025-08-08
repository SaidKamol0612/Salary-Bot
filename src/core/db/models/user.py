from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .shift import Shift
    from .payout import Payout


class User(Base):
    tg_id = mapped_column(BigInteger())
    name: Mapped[str] = mapped_column(String(15))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    shifts: Mapped[list["Shift"]] = relationship(back_populates="user")
    payouts: Mapped[list["Payout"]] = relationship(back_populates="user")
