from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .shift import Shift


class ShiftRole(Base):
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    shift: Mapped["Shift"] = relationship(back_populates="shift_roles")
