

import requests
from aiogram import Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup)

from src.filters.is_private import IsPrivateFilter
from src.services import LimitClient, OrderClient

from .keyboards import order_buttons

order_client = OrderClient()
limit_client = LimitClient()
router = Router()
router.message.filter(IsPrivateFilter())
dp = Dispatcher()


def get_id_from_caption(caption: str) -> int:
    try:
        order_id = int(caption.split("N")[1].split()[0])
        return order_id
    except:
        return None


def get_order_buttons(order_list, prefix=""):
    if order_list:
        buttons = []
        row = []

        for index, i in enumerate(order_list, start=1):
            button = InlineKeyboardButton(
                text=f"📋 Buyurtma N{i['id']} ({i['dmtt']['name']})",
                callback_data=f"order_{prefix}_{i['id']}"
            )

            row.append(button)

            # Har 2 ta tugmadan keyin yangi qatorga o'tkaz
            if len(row) == 2:
                buttons.append(row)
                row = []

        # Agar oxirgi qatorda 1 ta tugma qolsa
        if row:
            buttons.append(row)

        return buttons
    return []


async def send_order_list(message: Message,  order_list, prefix=""):
    if order_list:
        buttons = get_order_buttons(order_list, prefix)
        buttons.append([InlineKeyboardButton(
            text="🔙 Orqaga", callback_data="back")])

        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Buyurtmani tanlang:", reply_markup=reply_markup)
    else:
        await message.answer("🙅🏻‍♂️ Sizda buyurtmalar mavjud emas", reply_markup=order_buttons)


async def edit_order_list(callback_query: CallbackQuery,  order_list, prefix=""):
    buttons = get_order_buttons(order_list, prefix)
    buttons.append([InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("Buyurtmani tanlang:\n", reply_markup=reply_markup)
