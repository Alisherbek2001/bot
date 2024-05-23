from aiogram.fsm.state import State, StatesGroup


class Company(StatesGroup):
    name = State()
    adress = State()
    phone_number = State()
    stir = State()
    confirm = State()


class Delete_Company(StatesGroup):
    name = State()


class AcceptedOrder(StatesGroup):
    id = State()
    confirm = State()


class ActiveOrder(StatesGroup):
    id = State()


class RejectedOrder(StatesGroup):
    id = State()


class ProgressOrder(StatesGroup):
    id = State()
    confirm = State()


class DocumentOrder(StatesGroup):
    id = State()
