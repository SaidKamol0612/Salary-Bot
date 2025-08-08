from enum import StrEnum


class ShiftType(StrEnum):
    NIGHT = "night"
    DAY = "day"


# ShiftType.NIGHT.name.title() -> Night
# ShiftType.NIGHT.value -> night
