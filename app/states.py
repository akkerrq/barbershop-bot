from aiogram.fsm.state import State, StatesGroup

class BookingState(StatesGroup):
    choose_service = State()
    choose_date = State()
    enter_name = State()
    enter_phone = State()

class BossServiceState(StatesGroup):
    add_name = State()
    add_description = State()
    add_price = State()
    edit_price = State()