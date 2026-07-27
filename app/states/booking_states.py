from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    select_service = State()
    select_master = State()
    select_date = State()
    select_time = State()
    input_phone = State()
    input_comment = State()
    confirm = State()
