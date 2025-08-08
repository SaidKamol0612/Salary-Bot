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
            date = shift.date.strftime("%d.%m.%Y")
            duration_hours = _get_shift_duration(shift.start_time, shift.end_time)
            duration = f"{shift.start_time} - {shift.end_time} | {duration_hours} soat"
            type_icon = "☀️ Kunduzgi" if shift.shift_type == "day" else "🌙 Tungi"

            roles = []

            shift_roles = await ShiftRoleCRUD.get_shift_roles(session, shift.id)
            for sh_role in shift_roles:
                role = await RoleCRUD.get_role_by_id(session, sh_role.role_id)
                roles.append(
                    {
                        "name": role.name.name,
                        "rate": (
                            role.rate_day
                            if shift.shift_type == "day"
                            else role.rate_night
                        ),
                    }
                )

            role_names = " ".join([role["name"].title() for role in roles])
            info = f"{type_icon} | {role_names}"

            if shift.bonus > 0:
                info += f"\n➕ Qo'shimcha: +{shift.bonus}"

            total = (
                sum(
                    (
                        (role["rate"] * duration)
                        if role["name"].title() != "Oshpaz"
                        else 50000
                    )
                    for role in roles
                )
                + shift.bonus
            )
            salary += total

            total_str = f"💵 Jami: {total}"

            report += f"📅 {date}\n" f"🕒 {duration}\n" f"{info}\n" f"{total_str}\n\n"

        total_payout = 0
        if len(payouts) > 0:
            report += "To'lo'vlar:\n"
            for payout in payouts:
                report += (
                    f"\t💵 {payout.paid_at} -> {payout.amount} miqdorda to'lo'v.\n"
                )
                report += f"\tNote: {payout.note}\n"
                total_payout += payout.amount

        report += (
            "\n<b>📌 Yakuniy natija:</b>\n"
            f"<b>Umumiy oylik:</b> {salary} so'm\n"
            f"<b>Ummumiy to'langan:</b> {total_payout} so'm\n"
            f"<b>📊 Qoldik oylik:</b> {salary - total_payout} so'm"
        )

        return report
