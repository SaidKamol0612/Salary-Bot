from typing import TYPE_CHECKING
from datetime import time, date as py_date

from sqlalchemy import ForeignKey, Enum, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums import ShiftType

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .shift_role import ShiftRole


class Shift(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[py_date] = mapped_column(Date)
    start_time: Mapped[time]
    end_time: Mapped[time]
    shift_type: Mapped[ShiftType] = mapped_column(
        Enum(ShiftType, native_enum=False), nullable=False
    )
    bonus: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="shifts")
    shift_roles: Mapped[list["ShiftRole"]] = relationship(back_populates="shift")
