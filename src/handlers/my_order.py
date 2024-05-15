from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (KeyboardButton, Message,
                           ReplyKeyboardMarkup)
from src.filters.is_private import IsPrivateFilter

from src.handlers.keyboards import order_document
from src.handlers.schemas import OrderResponse
from src.handlers.states import Document_order
from src.handlers.utils import create_facture
from api import (get_order_accepted_api, get_order_id_api,
                 get_order_inprogress_api, get_order_pending_api,
                 get_order_rejected_api,
                 get_product_prices, post_order_in_accepted_api,
                 post_order_in_progress_api, post_order_rejected_api)
from .keyboards import (COMFIRM_BUTTON_NAME, check_buttons_in_progress, confirm_buttons,
                        firm_buttons, order_buttuns)
from .states import (Accepted_Order, Active_Order, Progress_order, Rejected_order)

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
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot += f"Buyurtma: {id}"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot, reply_markup=confirm_buttons)
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
            # response = get_order_id_api(id)
            # if response.status_code == 200:
            #     doc = DocxTemplate("src/temp.docx")
            #     data_list = response.json()
            #     if data_list:

            #         data = {
            #             "company_name": data_list["company"]["name"],
            #             "dmtt_name": data_list["dmtt"]["name"],
            #             "dmtt_address": data_list["dmtt"]["address"],
            #             "company_phone": data_list["company"]["phone_number"],
            #             "items": [
            #                 [item.get("product_name"),item.get('count')]
            #                 for item in data_list.get("items")
            #             ]
            #         }
            #         file_stream = io.BytesIO()
            #         doc.render(context=data)
            #         doc.save(file_stream)
            #         file_stream.seek(0)
            #         dd = BufferedInputFile(file_stream.read(), filename="test.docx")
            #         await message.answer_document(dd)
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
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot += f"Buyurtma: {id}\n"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot)


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
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot += f"Buyurtma: {id}\n"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot)


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
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot += f"Buyurtma: {id}\n"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot, reply_markup=check_buttons_in_progress)
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


@router.message(F.text == "🔙 Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=firm_buttons)


@router.message(F.text == order_document)
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
                "Ko'rish kerak bo'lgan buyurtmani tanlang : ", reply_markup=reply_markup
            )
            await state.set_state(Document_order.id)
        else:
            await message.answer(
                "🙅🏻‍♂️ Sizda faol buyurtmalar yo'q", reply_markup=order_buttuns
            )
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttuns)


@router.message(Document_order.id)
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
        product_response = get_product_prices(
            tg_user_id=telegram_id)
        if response.status_code == 200 and product_response.status_code == 200:
            data = OrderResponse.model_validate(response.json())
            price_data = {item['name']: {'price': item['price'],
                                         'measure': item['measure']} for item in product_response.json()}
            buf_file = create_facture(id, data, price_data)
            await message.answer_document(buf_file, reply_markup=order_buttuns)
        await message.answer("Menyu", reply_markup=order_buttuns)
        await state.clear()