import threading
from asyncio import create_task, run, sleep

import requests
from aiogram import Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from fastapi import BackgroundTasks

from api import (get_order_accepted_api, get_order_id_api,
                 get_order_inprogress_api, get_order_pending_api,
                 get_order_rejected_api, get_product_prices,
                 post_order_in_accepted_api, post_order_in_progress_api,
                 post_order_rejected_api)
from src.config import CHANNEL_ID
from src.filters.is_private import IsPrivateFilter
from src.handlers.keyboards import (faktura_document, order_document,
                                    order_document_without_price,
                                    refresh_db_command)
from src.handlers.schemas import FacturaLimitInfo, OrderResponse
from src.handlers.utils import (create_facture, create_facture_without_price,
                                create_full_facture, get_order_as_list)
from src.services import LimitClient, OrderClient

from .keyboards import (COMFIRM_BUTTON_NAME, buttun1,
                        check_buttons_in_progress, confirm_buttons,
                        firm_buttons, order_buttons)
from .states import AcceptedOrder, ActiveOrder, ProgressOrder, RejectedOrder

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


async def send_order_list(message: Message, state: FSMContext, order_list, next_state):
    if order_list:
        buttons = [[KeyboardButton(
            text=f"📋 Buyurtma N{i['id']} ({i['dmtt']['name']})")] for i in order_list]
        buttons.append([KeyboardButton(text="🔙 Orqaga")])
        reply_markup = ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True)
        await message.answer("Buyurtmani tanlang:", reply_markup=reply_markup)
        await state.set_state(next_state)
    else:
        await message.answer("🙅🏻‍♂️ Sizda buyurtmalar mavjud emas", reply_markup=order_buttons)


@router.message(F.text == "📋 Buyurtmalarim")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=order_buttons)


@router.message(F.text == "🆕 Yangi buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    """
        yangi buyurtmalar ro'yhati
    """
    telegram_id = message.from_user.id
    response = order_client.get_orders_pending(tg_user_id=telegram_id)
    data = response
    await send_order_list(message, state, data, AcceptedOrder.id)


@router.message(AcceptedOrder.id)
async def get_or_reject_order(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttons)
        await state.clear()
    else:
        order_id = get_id_from_caption(message.text)
        if not order_id:
            return await message.answer("Bosh menyu", reply_markup=order_buttons)
        await state.update_data(id=order_id)
        response = get_order_id_api(id=order_id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, order_id)
            await message.answer(malumot, reply_markup=confirm_buttons, parse_mode=ParseMode.HTML)
            await state.set_state(AcceptedOrder.confirm)


@router.message(AcceptedOrder.confirm)
async def post_order_to_in_progress(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttons)
        await state.clear()
    elif message.text == COMFIRM_BUTTON_NAME:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_in_progress_api(
            order_id=id, tg_user_id=telegram_id)
        if response.status_code == 200:
            await message.answer(
                f"✅ Javobingiz qabul qilindi",
                reply_markup=order_buttons,
            )
            await state.clear()
        else:
            await message.answer("Xatolik yuz berdi", reply_markup=order_buttons)
        await state.clear()
    else:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_rejected_api(order_id=id, tg_user_id=telegram_id)
        if response.status_code == 200:
            await message.answer(
                "✅ Javobingiz qabul qilindi", reply_markup=order_buttons
            )
        else:
            await message.answer("Xatolik yuz berdi", reply_markup=order_buttons)
        await state.clear()


@router.message(F.text == "✅ Bajarilgan buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_accepted_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        await send_order_list(message, state, data, ActiveOrder.id)
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)


@router.message(ActiveOrder.id)
async def get_order_detail(message: Message, state: FSMContext):
    """
        detail ko'rish
    """
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttons)
        await state.clear()
    else:
        order_id: int = get_id_from_caption(message.text)
        if not order_id:
            return await message.answer("Bosh menyu", reply_markup=order_buttons)
        response = get_order_id_api(id=order_id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, order_id)
            await message.answer(malumot, parse_mode=ParseMode.HTML)


@router.message(F.text == "🚫 Rad qilingan buyurtmalar")
async def get_rejected_orders_bot(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_rejected_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        await send_order_list(message, state, data, RejectedOrder.id)
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttons)


@router.message(RejectedOrder.id)
async def get_order_detail_rejected(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttons)
        await state.clear()
    else:
        order_id = get_id_from_caption(message.text)
        if not order_id:
            return await message.answer("Bosh menyu", reply_markup=order_buttons)
        response = get_order_id_api(id=order_id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, order_id)
            await message.answer(malumot, parse_mode=ParseMode.HTML)


@router.message(F.text == "🚛 Faol buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_inprogress_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        await send_order_list(message, state, data, ProgressOrder.id)

    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttons)


@router.message(ProgressOrder.id)
async def get_order_detail_in_progress(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttons)
        await state.clear()
    else:
        order_id = get_id_from_caption(message.text)
        if not order_id:
            return await message.answer("Bosh menyu", reply_markup=order_buttons)
        await state.update_data(id=order_id)

        response = get_order_id_api(id=order_id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, order_id)
            await message.answer(malumot, reply_markup=check_buttons_in_progress, parse_mode=ParseMode.HTML)
            await state.set_state(ProgressOrder.confirm)


@router.message(ProgressOrder.confirm)
async def post_order_to_acceted(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttons)
    else:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_in_accepted_api(
            order_id=id, tg_user_id=telegram_id)
        if response.status_code == 200:
            await message.answer(
                "✅ Javobingiz qabul qilindi", reply_markup=order_buttons
            )
        else:
            await message.answer(
                f"Xatolik yuz berdi",
                reply_markup=order_buttons,
            )
    await state.clear()


# by oxirida bo'lishi shart


@router.message(F.text == "🔙 Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=buttun1)


@router.message(F.text == refresh_db_command)
async def result(message: Message):
    await message.answer("Qabul qilindi biroz kuting ...", reply_markup=order_buttons)
    url = "http://api.mydmtt.uz/bot/limit-refresh"
    params = {
        "tg_user_id": message.from_user.id
    }
    requests.post(url, params=params)
