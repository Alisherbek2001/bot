from aiogram.fsm.state import StatesGroup,State

class Company(StatesGroup):
    name = State()
    adress = State()
    phone_number = State()
    stir = State()
    confirm = State()

class Delete_Company(StatesGroup):
    name = State()

class Accepted_Order(StatesGroup):
    id = State()


class Active_Order(StatesGroup):
    id = State()

class Rejected_order(StatesGroup):
    id = State()

class Progress_order(StatesGroup):
    id = State()
    confirm = State()