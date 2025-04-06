

import requests
from aiogram import Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup)

from api import (get_order_accepted_api, get_order_id_api,
                 get_order_inprogress_api, get_order_rejected_api,
                 post_order_in_accepted_api, post_order_in_progress_api,
                 post_order_rejected_api)
from src.filters.is_private import IsPrivateFilter
from src.handlers.functions import edit_order_list, send_order_list
from src.handlers.keyboards import refresh_db_command
from src.handlers.utils import get_order_as_list
from src.services import LimitClient, OrderClient

from .keyboards import (buttun1, check_buttons_in_progress, firm_buttons,
                        get_confirm_buttons, get_in_progress_buttons,
                        order_buttons)
from .states import AcceptedOrder, ProgressOrder, RejectedOrder

order_client = OrderClient()
limit_client = LimitClient()
router = Router()
router.message.filter(IsPrivateFilter())
dp = Dispatcher()


# --------------------------------------------------------------
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
    await send_order_list(message,  data, prefix="pending")


@router.callback_query(F.data.startswith("order_pending"))
async def get_or_reject_order(callback_query: CallbackQuery):

    order_id = callback_query.data.split("_")[-1]

    # await state.update_data(id=order_id)
    response = get_order_id_api(id=order_id)

    if response.status_code == 200:
        data = response.json()
        malumot = get_order_as_list(data, order_id)

        await callback_query.message.edit_text(
            malumot,
            reply_markup=get_confirm_buttons(order_id),
            parse_mode=ParseMode.HTML
        )

        # await state.set_state(AcceptedOrder.confirm)
    else:
        await callback_query.answer("Buyurtmani olishda xatolik", show_alert=True)


@router.callback_query(F.data == "back_active_orders")
async def get_new_orders(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id
    response = order_client.get_orders_pending(tg_user_id=telegram_id)
    data = response
    await edit_order_list(callback_query, data, prefix="pending")


@router.callback_query(F.data.startswith("confirm_order_"))
async def post_order_to_in_progress(callback_query: CallbackQuery):
    order_id = callback_query.data.split("_")[2]
    telegram_id = callback_query.from_user.id
    response = post_order_in_progress_api(
        order_id=order_id, tg_user_id=telegram_id)
    if response.status_code == 200:
        await callback_query.answer(
            f"✅ Javobingiz qabul qilindi", show_alert=True,
            reply_markup=order_buttons,
        )
        response = order_client.get_orders_pending(tg_user_id=telegram_id)
        data = response
        await edit_order_list(callback_query, data, AcceptedOrder.id)

    else:
        await callback_query.answer("Xatolik yuz berdi", show_alert=True, reply_markup=order_buttons)


@router.callback_query(F.data.startswith("reject_order_"))
async def post_order_to_in_progress(callback_query: CallbackQuery):
    order_id = callback_query.data.split("_")[2]
    telegram_id = callback_query.from_user.id
    response = post_order_rejected_api(
        order_id=order_id, tg_user_id=telegram_id)
    if response.status_code == 200:
        await callback_query.answer(
            f"✅ Javobingiz qabul qilindi", show_alert=True,
            reply_markup=order_buttons,
        )
        response = order_client.get_orders_pending(tg_user_id=telegram_id)
        data = response
        await edit_order_list(callback_query, data, AcceptedOrder.id)

    else:
        await callback_query.answer("Xatolik yuz berdi", show_alert=True, reply_markup=order_buttons)
#  --------------------------------------------------------------------------------


@router.message(F.text == "✅ Bajarilgan buyurtmalar")
async def new_orders(message: Message):
    telegram_id = message.from_user.id
    response = get_order_accepted_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()[:10]
        await send_order_list(message, data, prefix="accepted")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)


@router.callback_query(F.data.startswith("order_accepted"))
async def get_order_detail(callback_query: CallbackQuery):
    """
        detail ko'rish
    """
    # print(callback_query.data)
    order_id: int = callback_query.data.split("_")[-1]
    if not order_id:
        return await callback_query.answer("Bosh menyu", reply_markup=order_buttons)
    response = get_order_id_api(id=order_id)
    if response.status_code == 200:
        data = response.json()
        malumot = get_order_as_list(data, order_id)
        await callback_query.message.edit_text(malumot, parse_mode=ParseMode.HTML)


@router.message(F.text == "🚫 Rad qilingan buyurtmalar")
async def get_rejected_orders_bot(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_rejected_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        await send_order_list(message,  data, "rejected")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttons)


@router.callback_query(F.data.startswith("order_rejected"))
async def get_order_detail_rejected(callback_query: CallbackQuery, state: FSMContext):

    order_id = callback_query.data.split("_")[-1]
    if not order_id:
        return await callback_query.answer("Bosh menyu", reply_markup=order_buttons)
    response = get_order_id_api(id=order_id)
    if response.status_code == 200:
        data = response.json()
        malumot = get_order_as_list(data, order_id)
        await callback_query.answer(malumot, parse_mode=ParseMode.HTML)


@router.message(F.text == "🚛 Faol buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_inprogress_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        await send_order_list(message,  data, "in_progress")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttons)


@router.callback_query(F.data.startswith("order_in_progress"))
async def get_order_detail_in_progress(callback_query: CallbackQuery, state: FSMContext):
    order_id = callback_query.data.split("_")[-1]

    if not order_id:
        return await callback_query.answer("Bosh menyu", reply_markup=order_buttons)

    response = get_order_id_api(id=order_id)
    if response.status_code == 200:
        data = response.json()
        malumot = get_order_as_list(data, order_id)
        await callback_query.message.edit_text(malumot, reply_markup=get_in_progress_buttons(order_id),
                                               parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("mark_as_done_"))
async def post_order_to_acceted(callback_query: CallbackQuery):
    """
        buyurtmani yetkazish qilish
    """

    telegram_id = callback_query.from_user.id
    order_id = callback_query.data.split("_")[-1]
    response = post_order_in_accepted_api(
        order_id=order_id, tg_user_id=telegram_id)
    if response.status_code == 200:
        await callback_query.answer(
            "✅ Javobingiz qabul qilindi", show_alert=True, reply_markup=order_buttons
        )
        
    else:
        await callback_query.answer(
            f"Xatolik yuz berdi",
            reply_markup=order_buttons,
        )


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
