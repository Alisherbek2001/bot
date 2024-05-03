import io
from aiogram import types, Router, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from src.filters.is_private import IsPrivateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from api import (
    check_phone,
    get_company,
    create_company_api,
    delete_company_api,
    get_orders_acceptet_api,
    get_order_id_api,
    get_order_accepted_api,
    get_order_rejected_api,
    get_order_inprogress_api,
    post_order_in_progress_api,
    post_order_in_accepted_api,
    get_order_pending_api,
    post_order_rejected_api,
)
from .keyboards import (
    COMFIRM_BUTTON_NAME,
    contact_share_markup,
    buttun1,
    firm_buttons,
    order_buttuns,
    check_buttons,
    check_buttons_in_progress,
    confirm_buttons,
)
from .states import (
    Company,
    Delete_Company,
    Accepted_Order,
    Active_Order,
    Rejected_order,
    Progress_order,
)
from aiogram.types.input_file import BufferedInputFile
from docxtpl import DocxTemplate

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


@router.message(F.text == "🏛 Firmalarim")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=firm_buttons)


@router.message(F.text == "📋 Buyurtmalarim")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=order_buttuns)


@router.message(F.text == "⬅️ Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=buttun1)


@router.message(F.text == "🏛 Mening firmalarim")
async def result(message: Message):
    telegram_id = message.from_user.id
    response = get_company(tg_user_id=telegram_id)
    if response.status_code == 200:

        data = response.json()
        if len(data) > 0:
            for i in data:
                await message.answer(
                    f"🏛 Firmaning nomi : {i['name']}\n"
                    f"🏠 Joylashuvi : {i['address']}\n"
                    f"☎️ Telefon raqami : {i['phone_number']}\n"
                    f"📝 Stir : {i['stir']}",
                    reply_markup=firm_buttons,
                )
        else:
            await message.answer(
                "Sizda firmalar mavjud emas : ", reply_markup=firm_buttons
            )


@router.message(F.text == "➕ Firma qo'shish")
async def result(message: Message, state: FSMContext):
    await message.answer("Firmaning nomini kiriting : ")
    await state.set_state(Company.name)


@router.message(Company.name)
async def create_company(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Manzilni kiriting : ")
    await state.set_state(Company.adress)


@router.message(Company.adress)
async def create_company(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Telefon raqamini kiriting : ")
    await state.set_state(Company.phone_number)


@router.message(Company.phone_number)
async def create_company(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Stir raqamini kiriting : ")
    await state.set_state(Company.stir)


@router.message(Company.stir)
async def create_company(message: Message, state: FSMContext):
    await state.update_data(stir=message.text)
    await message.answer("Ma'lumotlaringizni to'griligini tekshiring: ")
    data = await state.get_data()
    await message.answer(
        f"🏛 Firmaning nomi : {data['name']}\n"
        f"🏠 Joylashuvi : {data['address']}\n"
        f"☎️ Telefon raqami : {data['phone_number']}\n"
        f"📝 Stir : {data['stir']}",
        reply_markup=check_buttons,
    )
    await state.set_state(Company.confirm)


@router.message(Company.confirm)
async def create_company_bot(message: Message, state: FSMContext):
    if message.text == "✅ Ha":
        data = await state.get_data()
        tg_user_id = message.from_user.id
        name = data["name"]
        address = data["address"]
        phone_number = data["phone_number"]
        stir = data["stir"]
        response = create_company_api(
            tg_user_id=tg_user_id,
            name=name,
            phone_number=phone_number,
            address=address,
            stir=stir,
        )
        if response.status_code == 200:
            await message.answer(
                "✅ Firma muvaffaqiyatli yaratildi", reply_markup=firm_buttons
            )
        else:
            await message.answer("😭 Xatolik yuz berdi. Qaytadan urinib ko'ring !")
        await state.clear()
    else:
        await message.answer("Tanlovingiz uchun raxmat ! ", reply_markup=firm_buttons)
        await state.clear()


@router.message(F.text == "❌ Firma o'chirish")
async def delete_company(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_company(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        buttons = []
        for i in data:
            buttons.append([KeyboardButton(text=i["name"])])
        buttons.append([KeyboardButton(text="◀️ Orqaga")])
        reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(
            "O'chirilishi kerak bo'lgan kompaniyani birini tanlang",
            reply_markup=reply_markup,
        )
        await state.set_state(Delete_Company.name)
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)


@router.message(Delete_Company.name)
async def company_delete(message: Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=firm_buttons)
        await state.clear()
    else:
        await state.update_data(name=message.text)
        telegram_id = message.from_user.id
        response = get_company(tg_user_id=telegram_id)
        if response.status_code == 200:
            data = response.json()
            is_founded = False
            for i in data:
                state_data = await state.get_data()
                name = state_data["name"]
                if name == i["name"]:
                    id = i["id"]
                    tg_user_id = telegram_id
                    delete_company_api(id=id, tg_user_id=tg_user_id)
                    await message.answer(
                        "O'chirish muvaffaqiyatli bajarildi  : ",
                        reply_markup=firm_buttons,
                    )
                    is_founded = True
                    break
            if not is_founded:
                await message.answer(
                    "Kechirasiz bunday nomdagi firma topilmadi",
                    reply_markup=firm_buttons,
                )


@router.message(F.text == "◀️ Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=firm_buttons)


# Yangi buyurtmalarni ko'rish

@router.message(F.text == "🆕 Yangi buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_pending_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        buttons = []
        for i in data:
            buttons.append([KeyboardButton(text=f"📋 Buyurtma: {i['dmtt']['name']} {i['id']}")])
        buttons.append([KeyboardButton(text="🔙 Orqaga")])
        reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Buyurtmani tanlang : ", reply_markup=reply_markup)
        await state.set_state(Accepted_Order.id)
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=order_buttuns)

# orderni qabul qilish yoki rad etish
@router.message(Accepted_Order.id)
async def get_or_reject_order(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split()[-1]
        await state.update_data(id=id)
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot += f"📋 Buyurtma: {id}"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot, reply_markup=confirm_buttons)
            await state.set_state(Accepted_Order.confirm)

# orderni qabul qilish
@router.message(Accepted_Order.confirm)
async def post_order_to_in_progress(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    elif message.text == COMFIRM_BUTTON_NAME:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_in_progress_api(order_id=id, tg_user_id=telegram_id)
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
                buttons.append([KeyboardButton(text=f"📋 Buyurtma: {i['dmtt']['name']} {i['id']}")])
            buttons.append([KeyboardButton(text="🔙 Orqaga")])
            reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
            await message.answer(
                "Ko'rish kerak bo'lgan bog'chani tanlang : ", reply_markup=reply_markup
            )
            await state.set_state(Active_Order.id)
        else:
            await message.answer("Sizda bajarilgan buyurtmalar mavjus emas")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)

# order itemslarni ko'rish
@router.message(Active_Order.id)
async def get_order_detail(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split()[-1]
        await state.update_data(id=id)
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot += f"📋 Buyurtma: {id}\n"
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
                buttons.append([KeyboardButton(text=f"📋 Buyurtma: {i['dmtt']['name']} {i['id']}")])
            buttons.append([KeyboardButton(text="🔙 Orqaga")])
            reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
            await message.answer("Buyurtmani tanlang  : ", reply_markup=reply_markup)
            await state.set_state(Rejected_order.id)
        else:
            await message.answer("Sizda rad qilingan buyurtmalar yo'q")
    else:
        await message.answer("Xatolik yuz berdi !", reply_markup=firm_buttons)

# get order detail
@router.message(Rejected_order.id)
async def get_order_detail_rejected(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split()[-1]
        await state.update_data(id=id)
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot+= f"📋 Buyurtma: {id}\n"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot)

# Faol buyurtmalani button
@router.message(F.text == "🚛 Faol buyurtmalar")
async def new_orders(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    response = get_order_inprogress_api(tg_user_id=telegram_id)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            buttons = []
            for i in data:
                buttons.append([KeyboardButton(text=f"📋 Buyurtma: {i['dmtt']['name']} {i['id']}")])
            buttons.append([KeyboardButton(text="🔙 Orqaga")])
            reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
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

# faol buyurtmani detail ko'rish
@router.message(Progress_order.id)
async def get_order_detail_in_progress(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
        await state.clear()
    else:
        caption = message.text
        id = caption.split()[-1]
        await state.update_data(id=id)
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = get_order_id_api(id=id)
        if response.status_code == 200:
            data = response.json()
            malumot = f"🏛 Bog'cha {data['dmtt']['name']}\n"
            malumot+= f"📋 Buyurtma: {id}\n"
            for i in data["items"]:
                malumot += f"{i['product_name']} - {i['count']}\n"
            await message.answer(malumot, reply_markup=check_buttons_in_progress)
            await state.set_state(Progress_order.confirm)

# faol buyurtmani bajarildi deb belgilash qilish
@router.message(Progress_order.confirm)
async def post_order_to_acceted(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Kerakli bo'limni tanlang !", reply_markup=order_buttuns)
    else:
        telegram_id = message.from_user.id
        state_data = await state.get_data()
        id = state_data["id"]
        response = post_order_in_accepted_api(order_id=id, tg_user_id=telegram_id)
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


router.message(F.text == "🔙 Orqaga")


async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=firm_buttons)
