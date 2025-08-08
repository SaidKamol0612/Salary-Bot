from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    request_name = State()


class AdminState(StatesGroup):
    choose_worker_for_report = State()
    
    choose_worker_for_payout = State()
    request_amount = State()
    request_note = State()