from aiogram.fsm.state import State, StatesGroup


class BookingState(StatesGroup):
    name = State()

    phone = State()

    service = State()

    employee = State()

    date = State()

    time = State()

    comment = State()
