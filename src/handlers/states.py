from aiogram.fsm.state import StatesGroup,State

class Company(StatesGroup):
    name = State()
    adress = State()
    phone_number = State()
    stir = State()
    confirm = State()

class Delete_Company(StatesGroup):
    name = State()

