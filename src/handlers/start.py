
from aiogram import Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from src.filters.is_private import IsPrivateFilter

from api import check_phone
from .keyboards import buttun1,contact_share_markup


router = Router()
router.message.filter(IsPrivateFilter())
dp = Dispatcher()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(f"Assalomu alaykum {message.from_user.first_name}")
    await message.answer(
        f"Iltimos telefon raqamingizni yuboring !", reply_markup=contact_share_markup
    )


@router.message(Command("menu"))
async def start_handler(message: types.Message):
    await message.answer("Kerakli bo'limni tanlang : ", reply_markup=buttun1)


@router.message(F.contact)
async def get_contact(message: Message):
    phone_number = message.contact.phone_number
    if phone_number[0] == "+":
        phone_number = phone_number
    else:
        phone_number = f"+{phone_number}"
    telegram_id = str(message.from_user.id)
    response = check_phone(phone_number=phone_number, tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        first_name = data["first_name"]
        last_name = data["last_name"]

        await message.answer(f"Xush kelibsiz : <b>{first_name} {last_name}</b>")
        await message.answer("Kerakli bo'limni tanlang : ", reply_markup=buttun1)
    else:
        await message.answer("Kechirasiz siz bu botdan foydalana olmaysiz !")





