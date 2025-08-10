import re
from datetime import datetime, time, timedelta
from core.enums import Role

ROLE_CODES = {
    Role.XAMIRCHI.value: Role.XAMIRCHI.name,
    Role.PECHKACHI.value: Role.PECHKACHI.name,
    Role.TERUVCHI.value: Role.TERUVCHI.name,
    Role.OSHPAZ.value: Role.OSHPAZ.name,
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
    night_start = time(18, 0)
    night_end = time(6, 0)

    today = datetime.today().date()
    dt_start = datetime.combine(today, start)
    dt_end = datetime.combine(today, end)

    if dt_end <= dt_start:
        dt_end += timedelta(days=1)

    night_range = (
        datetime.combine(today, night_start),
        datetime.combine(today + timedelta(days=1), night_end),
    )

    overlap = dt_start < night_range[1] and dt_end > night_range[0]
    return "night" if overlap else "day"


class RecordParser:
    @staticmethod
    def parse(text: str) -> dict:
        try:
            raw = re.sub(r"[|/\\]", "|", text)
            raw = re.sub(r"–|—|-", "-", raw)
            parts = [p.strip() for p in raw.strip().split("|")]

            if len(parts) < 3:
                raise ValueError("Format must be: name | time/number | role")

            name_raw, second_raw, role_raw = parts[0], parts[1], parts[2]
            name = name_raw.title()

            if re.match(r"^\d+(\.\d+)?$", second_raw):
                number = float(second_raw) if "." in second_raw else int(second_raw)
                roles = _parse_role_codes(role_raw)
                return {
                    "name": name,
                    "number": number,
                    "shift_type": "night",
                    "roles": roles,
                }
            elif re.match(r".+?-.+", second_raw):
                match = re.match(r"(.+?)-(.+)", second_raw)
                if not match:
                    raise ValueError("Invalid time format. Example: 08:00–16:00")

                start_str = _normalize_time_string(match.group(1))
                end_str = _normalize_time_string(match.group(2))
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()

                shift_type = _determine_shift_type(start_time, end_time)
                roles = _parse_role_codes(role_raw)

                return {
                    "name": name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "shift_type": shift_type,
                    "roles": roles,
                }
            else:
                raise ValueError("Second field must be either a number or a time range")
        except Exception as e:
            raise ValueError(f"Parse error: {e}")


# Testcases
# TEST_CASES = [
#     "Алихан | 08:00–16:00 | XO",  # Day shift
#     "Алихан | 22:00–06:00 | T",   # Night shift by time
#     "Алихан | 8 | XO",            # Night by num
#     "Алихан | 8.5 | P",           # Night by num with point
# ]

# for rec in TEST_CASES:
#     print(RecordParser.parse(rec))
