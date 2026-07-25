from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):

    name = State()

    phone = State()

    service = State()

    employee = State()

    date = State()

    time = State()

    comment = State()