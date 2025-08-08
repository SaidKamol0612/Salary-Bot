import re
from datetime import datetime, time, timedelta

from core.enums import Role

ROLE_CODES = {
    Role.XAMIRCHI.value: Role.XAMIRCHI.name,
    Role.PECHKACHI.value: Role.PECHKACHI.name,
    Role.TERUVCHI.value: Role.TERUVCHI.name,
    Role.OSHPAZ.value: Role.OSHPAZ.name,
    # Add more if necessary
}


def _normalize_time_string(t: str) -> str:
    t = re.sub(r"[^\d]", ":", t)
    parts = [p.zfill(2) for p in t.split(":") if p]
    if len(parts) == 1:
        parts.append("00")
    return ":".join(parts[:2])


def _parse_role_codes(code: str) -> list:
    roles = []
    for c in code.upper():
        if c in ROLE_CODES:
            roles.append(ROLE_CODES[c])
        else:
            raise ValueError(f"Unknown role code: '{c}'")
    return roles


def _determine_shift_type(start: time, end: time) -> str:
    night_start = time(22, 0)
    night_end = time(6, 0)

    today = datetime.today().date()
    dt_start = datetime.combine(today, start)
    dt_end = datetime.combine(today, end)

    if dt_end <= dt_start:
        dt_end += timedelta(days=1)

    night_range_1 = (
        datetime.combine(today, night_start),
        datetime.combine(today + timedelta(days=1), night_end),
    )

    overlap = dt_start < night_range_1[1] and dt_end > night_range_1[0]

    return "night" if overlap else "day"


class RecordParser:
    @staticmethod
    def parse_shift_message(text: str) -> dict:
        try:
            raw = re.sub(r"[|/\\]", "|", text)
            raw = re.sub(r"–|—|-", "-", raw)
            parts = [p.strip() for p in raw.strip().split("|")]

            if len(parts) < 3:
                raise ValueError("Format must be: name | time | role [| bonus]")

            name_raw, time_raw, role_raw = parts[0], parts[1], parts[2]
            bonus_raw = parts[3] if len(parts) >= 4 else "0"

            name = name_raw.title()

            match = re.match(r"(.+?)[-–—](.+)", time_raw)
            if not match:
                raise ValueError("Invalid time format. Example: 08:00–16:00")

            start_str = _normalize_time_string(match.group(1))
            end_str = _normalize_time_string(match.group(2))
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()

            shift_type = _determine_shift_type(start_time, end_time)
            roles = _parse_role_codes(role_raw)

            bonus_cleaned = bonus_raw.replace("+", "").replace("сум", "").strip()
            bonus = int(re.sub(r"[^\d]", "", bonus_cleaned) or "0")

            return {
                "name": name,
                "start_time": start_time,
                "end_time": end_time,
                "shift_type": shift_type,  # "day" or "night"
                "roles": roles,
                "bonus": bonus,
            }

        except Exception as e:
            raise ValueError(f"Parse error: {e}")


# Testcase
TEST_CASES = [
    # NOTE: Correct entries!
    # Day shifts
    "Алихан | 08:00–16:00 | X | +500",
    "Алихан | 8.00 - 16.00 | XO | 1000",
    "Алихан | 9-18 | O | сум 200",
    "Алихан | 08:00 — 16:00 | T |",
    "Алихан | 8:00—16:00 | TP",
    # Night shifts
    "Алихан | 22:00–06:00 | T",
    "Алихан | 21.00 - 02.00 | XP | +300",
    "Алихан | 23-8 | O | 0",
    "Алихан | 0:00 — 06:00 | TO",
    # Different separators
    "Алихан / 08-00–16:00 / P / 500",
    "Алихан \ 09:00 – 17:00 \ XT / +400",
    "Алихан | 10:00 - 19.00 | OX | ",
    # Roles without bonus
    "Алихан | 08:00–16:00 | TX",
    "Алихан | 10:00 - 18:00 | P",
    # NOTE: Incorrect entries!
    # Not enough parts
    "Алихан | 08:00–16:00",
    "Алихан | PT | +500",
    "08:00–16:00 | T | 500",
    # Time error
    "Алихан | восьмь - шестнадцать | P | +500",
    "Алихан | 08:00 - | X | +500",
    "Алихан | - 16:00 | T | +500",
    # Role error
    "Алихан | 08:00–16:00 | D | +500",
    "Алихан | 08:00–16:00 | TXE | 100",
    # Fully incorrect record
    "Работал до 5, повар, 1000",
    "08:00–16:00 Кассир 500",
]


class _RecordParserTester:
    @staticmethod
    def test_record_parser():
        for i, record in enumerate(TEST_CASES, 1):
            try:
                result = RecordParser.parse_shift_message(record)
                print(f"[{i}] ✅ Success: {record} -> {result}")
            except ValueError as e:
                print(f"[{i}] ⚠️ Error: {e}")


# import argparse

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Shift record parser CLI")
#     parser.add_argument("command", choices=["test"], help="Command to run")

#     args = parser.parse_args()

#     if args.command == "test":
#         _RecordParserTester.test_record_parser()
