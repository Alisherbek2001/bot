from aiogram import Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from api import (get_order_accepted_api, get_order_id_api,
                 get_order_inprogress_api, get_order_pending_api,
                 get_order_rejected_api, get_product_prices,
                 post_order_in_accepted_api, post_order_in_progress_api,
                 post_order_rejected_api)
from src.filters.is_private import IsPrivateFilter
from src.handlers.keyboards import order_document
from src.handlers.schemas import OrderResponse
from src.handlers.states import Document_order
from src.handlers.utils import create_facture, get_order_as_list
from src.services import OrderClient

from .keyboards import (COMFIRM_BUTTON_NAME, buttun1,
                        check_buttons_in_progress, confirm_buttons,
                        firm_buttons, order_buttuns)
from .states import (Accepted_Order, Active_Order, Progress_order,
                     Rejected_order)

order_client = OrderClient()
router = Router()
router.message.filter(IsPrivateFilter())
dp = Dispatcher()


@router.message(F.text == "📋 Buyurtmalarim")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=order_buttuns)


@router.message(F.text == "🆕 Yangi buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_pending_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        buttons = []
        for i in data:
            buttons.append(
                [KeyboardButton(text=f"📋 Buyurtma N{i['id']} ({i['dmtt']['name']})")])
        buttons.append([KeyboardButton(text="🔙 Orqaga")])
        reply_markup = ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True)
        await message.answer("Buyurtmani tanlang : ", reply_markup=reply_markup)
        await state.set_state(Accepted_Order.id)
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttuns)


@router.message(Accepted_Order.id)
async def get_or_reject_order(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split("N")[1].split()[0]
        await state.update_data(id=id)
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, id)
            await message.answer(malumot, reply_markup=confirm_buttons, parse_mode=ParseMode.HTML)
            await state.set_state(Accepted_Order.confirm)


@router.message(Accepted_Order.confirm)
async def post_order_to_in_progress(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    elif message.text == COMFIRM_BUTTON_NAME:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_in_progress_api(
            order_id=id, tg_user_id=telegram_id)
        if response.status_code == 200:
            await message.answer(
                f"✅ Javobingiz qabul qilindi {response.text}",
                reply_markup=order_buttuns,
            )
            await state.clear()
        else:
            await message.answer("Xatolik yuz berdi", reply_markup=order_buttuns)
        await state.clear()
    else:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_rejected_api(order_id=id, tg_user_id=telegram_id)
        if response.status_code == 200:
            await message.answer(
                "✅ Javobingiz qabul qilindi", reply_markup=order_buttuns
            )
        else:
            await message.answer("Xatolik yuz berdi", reply_markup=order_buttuns)
        await state.clear()


@router.message(F.text == "✅ Bajarilgan buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_accepted_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        buttons = []
        if len(data) > 0:
            for i in data:
                buttons.append(
                    [KeyboardButton(text=f"📋 Buyurtma N{i['id']} ({i['dmtt']['name']})")])
            buttons.append([KeyboardButton(text="🔙 Orqaga")])
            reply_markup = ReplyKeyboardMarkup(
                keyboard=buttons, resize_keyboard=True)
            await message.answer(
                "Ko'rish kerak bo'lgan bog'chani tanlang : ", reply_markup=reply_markup
            )
            await state.set_state(Active_Order.id)
        else:
            await message.answer("Sizda bajarilgan buyurtmalar mavjus emas")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)


@router.message(Active_Order.id)
async def get_order_detail(message: Message, state: FSMContext):
    """
        detail ko'rish 
    """
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split("N")[1].split()[0]
        await state.update_data(id=id)
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, id)
            await message.answer(malumot, parse_mode=ParseMode.HTML)


@router.message(F.text == "🚫 Rad qilingan buyurtmalar")
async def get_rejected_orders_bot(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_rejected_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            buttons = []
            for i in data:
                buttons.append(
                    [KeyboardButton(text=f"📋 Buyurtma N{i['id']} ({i['dmtt']['name']})")])
            buttons.append([KeyboardButton(text="🔙 Orqaga")])
            reply_markup = ReplyKeyboardMarkup(
                keyboard=buttons, resize_keyboard=True)
            await message.answer("Buyurtmani tanlang  : ", reply_markup=reply_markup)
            await state.set_state(Rejected_order.id)
        else:
            await message.answer("Sizda rad qilingan buyurtmalar yo'q")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)


@router.message(Rejected_order.id)
async def get_order_detail_rejected(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split("N")[1].split()[0]
        await state.update_data(id=id)
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, id)
            await message.answer(malumot, parse_mode=ParseMode.HTML)


@router.message(F.text == "🚛 Faol buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_inprogress_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            buttons = []
            for i in data:
                buttons.append(
                    [KeyboardButton(text=f"📋 Buyurtma N{i['id']} ({i['dmtt']['name']})")])
            buttons.append([KeyboardButton(text="🔙 Orqaga")])
            reply_markup = ReplyKeyboardMarkup(
                keyboard=buttons, resize_keyboard=True)
            await message.answer(
                "Ko'rish kerak bo'lgan bog'chani tanlang : ", reply_markup=reply_markup
            )
            await state.set_state(Progress_order.id)
        else:
            await message.answer(
                "🙅🏻‍♂️ Sizda faol buyurtmalar yo'q", reply_markup=order_buttuns
            )
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttuns)


@router.message(Progress_order.id)
async def get_order_detail_in_progress(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split("N")[1].split()[0]
        await state.update_data(id=id)
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = get_order_as_list(data, id)
            await message.answer(malumot, reply_markup=check_buttons_in_progress, parse_mode=ParseMode.HTML)
            await state.set_state(Progress_order.confirm)


@router.message(Progress_order.confirm)
async def post_order_to_acceted(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
    else:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_in_accepted_api(
            order_id=id, tg_user_id=telegram_id)
        if response.status_code == 200:
            await message.answer(
                "✅ Javobingiz qabul qilindi", reply_markup=order_buttuns
            )
        else:
            await message.answer(
                f"Xatolik yuz berdi",
                reply_markup=order_buttuns,
            )
    await state.clear()
    # state_data = await state.get_data()
    # id = state_data['id']


@router.message(F.text == order_document)
async def get_document_orders(message: Message, state: FSMContext):
    """
        yuk xati olish
    """
    telegram_id = message.from_user.id
    response = order_client.get_orders_in_progress(tg_user_id=telegram_id)
    data = response
    product_response = order_client.get_product_prices(
        tg_user_id=telegram_id)
    price_data = {item['name']: {'price': item['price'],
                                 'measure': item['measure']} for item in product_response}
    if len(data) > 0:
        for order in data:
            order_id = order['id']
            response = order_client.get_order_by_id(order_id=order_id)
            data = OrderResponse.model_validate(response)
            buffer_file = create_facture(order_id, data, price_data)
            await message.answer(buffer_file)
    else:
        await message.answer(
            "🙅🏻‍♂️ Sizda faol buyurtmalar yo'q", reply_markup=order_buttuns
        )


# by oxirida bo'lishi shart
@router.message(F.text == "🔙 Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=buttun1)
