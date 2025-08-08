from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import Role as RoleEnum

from .base import Base


class Role(Base):
    code: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, native_enum=False))
    rate_day: Mapped[int]
    rate_night: Mapped[int]
