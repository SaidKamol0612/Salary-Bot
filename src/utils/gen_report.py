from datetime import datetime, timedelta, time

from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models
from core.crud import ShiftRoleCRUD, RoleCRUD


def _get_shift_duration(start_time: time, end_time: time) -> float:
    today = datetime.today().date()
    start_dt = datetime.combine(today, start_time)
    end_dt = datetime.combine(today, end_time)

    if end_dt < start_dt:
        end_dt += timedelta(days=1)

    duration = end_dt - start_dt
    hours = duration.total_seconds() / 3600

    return round(hours, 1)


class ReportGenerator:
    @staticmethod
    async def gen_report(
        session: AsyncSession,
        worker: models.User,
        shifts: list[models.Shift],
        payouts: list[models.Payout],
        is_to_worker: bool = False,
    ) -> str:
        if is_to_worker:
            report = f"📋 <b>Siz</b>ning to'liq ish hisobotingiz\n"
        else:
            report = f"📋 <b>{worker.name}</b>ning to'liq ish hisoboti\n"

        report += "Ishlagan smenalar:\n"
        salary = 0
        for shift in shifts:
            date_str = shift.date.strftime("%d.%m.%Y")
            if shift.shift_type == "day":
                duration_hours = _get_shift_duration(shift.start_time, shift.end_time)
                duration_or_count = (
                    f"🕛 {shift.start_time} - {shift.end_time} | {duration_hours} soat"
                )
                type_icon = "☀️ Kunduzgi"
            else:
                duration_or_count = f"Xamirlar soni: {shift.count_dough}"
                type_icon = "🌙 Tungi"

            # Roles
            roles = []
            shift_roles = await ShiftRoleCRUD.get_shift_roles(session, shift.id)
            for sh_role in shift_roles:
                role = await RoleCRUD.get_role_by_id(session, sh_role.role_id)
                roles.append(
                    {
                        "name": role.name.name,
                        "rate_day": role.rate_day,
                        "rate_night": role.rate_night,
                    }
                )

            role_names = " ".join([role["name"].title() for role in roles])
            info = f"{type_icon} | {role_names}"

            if shift.bonus > 0:
                info += f"\n➕ Qo'shimcha: +{shift.bonus}"

            total = 0
            for role in roles:
                if role["name"].title() == "Oshpaz":
                    total += 50000
                else:
                    if shift.shift_type == "day":
                        total += int(role["rate_day"]) * int(duration_hours)
                    else:
                        total += int(role["rate_night"]) * int(shift.count_dough)

            total += int(shift.bonus)
            salary += total

            report += (
                f"📅 {date_str}\n"
                f"{duration_or_count}\n"
                f"{info}\n"
                f"💵 Jami: {total}\n\n"
            )

        total_payout = 0
        if payouts:
            report += "To'lo'vlar:\n"
            for payout in payouts:
                report += (
                    f"\t💵 {payout.paid_at.strftime('%d/%m/%Y')} : {payout.amount} miqdorda to'lo'v.\n"
                    f"\tNote: {payout.note}\n"
                )
                total_payout += int(payout.amount)

        report += (
            "\n<b>📌 Yakuniy natija:</b>\n"
            f"<b>Umumiy oylik:</b> {salary} so'm\n"
            f"<b>Umumiy to'langan:</b> {total_payout} so'm\n"
            f"<b>📊 Qoldik oylik:</b> {salary - total_payout} so'm"
        )

        return report

    @staticmethod
    async def calculate_shifts_total(
        session: AsyncSession,
        shifts: list[models.Shift],
        payouts: list[models.Payout],
    ) -> int:
        salary = 0
        for shift in shifts:
            if shift.start_time:
                duration_hours = _get_shift_duration(shift.start_time, shift.end_time)
            # Roles
            roles = []
            shift_roles = await ShiftRoleCRUD.get_shift_roles(session, shift.id)
            for sh_role in shift_roles:
                role = await RoleCRUD.get_role_by_id(session, sh_role.role_id)
                roles.append(
                    {
                        "name": role.name.name,
                        "rate_day": role.rate_day,
                        "rate_night": role.rate_night,
                    }
                )
            total = 0
            for role in roles:
                if role["name"].title() == "Oshpaz" and shift.shift_type == "day":
                    total += 50000
                elif shift.shift_type == "day":
                    total += int(role["rate_day"]) * int(duration_hours)
                else:
                    total += int(role["rate_night"]) * int(shift.count_dough)

            total += int(shift.bonus)
            salary += total
        total_payout = 0
        if payouts:
            for payout in payouts:
                total_payout += int(payout.amount)
        return salary - total_payout

    @staticmethod
    async def calculate_shift_total(
        session: AsyncSession,
        shift: models.Shift,
    ) -> int:
        # Calculate shift duration safely
        duration_hours = (
            _get_shift_duration(shift.start_time, shift.end_time)
            if shift.start_time and shift.end_time
            else 0
        )

        # Get roles assigned to this shift
        shift_roles = await ShiftRoleCRUD.get_shift_roles(session, shift.id)
        roles = []
        for sh_role in shift_roles:
            role = await RoleCRUD.get_role_by_id(session, sh_role.role_id)
            roles.append({
                "name": role.name.name,
                "rate_day": role.rate_day,
                "rate_night": role.rate_night,
            })

        # Calculate total salary
        total_salary = 0
        for role in roles:
            if role["name"].title() == "Oshpaz" and shift.shift_type == "day":
                total_salary += 50_000
            elif shift.shift_type == "day":
                total_salary += int(role["rate_day"]) * int(duration_hours)
            else:  # night shift
                total_salary += int(role["rate_night"]) * int(shift.count_dough or 0)

        # Add bonus once per shift
        total_salary += int(shift.bonus or 0)
        return total_salary

