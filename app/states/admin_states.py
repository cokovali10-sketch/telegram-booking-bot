from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    add_service_title = State()
    add_service_price = State()
    add_service_duration = State()
    add_master_name = State()
    add_master_phone = State()
