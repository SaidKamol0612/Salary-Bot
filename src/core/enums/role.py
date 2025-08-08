from enum import StrEnum


class Role(StrEnum):
    XAMIRCHI = "X"
    PECHKACHI = "P"
    TERUVCHI = "T"
    OSHPAZ = "O"


# Role.OSHPAZ.name.title() -> Oshpaz
# Role.OSHPAZ.value -> O
