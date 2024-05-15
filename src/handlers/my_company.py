from aiogram import Dispatcher, F, Router
from src.filters.is_private import IsPrivateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (KeyboardButton, Message,
                           ReplyKeyboardMarkup)
from api import (create_company_api, delete_company_api,
                 get_company)
from .keyboards import (check_buttons, firm_buttons, buttun1)
from .states import (Company, Delete_Company)

router = Router()
router.message.filter(IsPrivateFilter())
dp = Dispatcher()

@router.message(F.text == "🏛 Firmalarim")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=firm_buttons)


@router.message(F.text == "⬅️ Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=buttun1)


@router.message(F.text == "◀️ Orqaga")
async def result(message: Message):
    await message.answer("Kerakli bo'limni tanlang", reply_markup=firm_buttons)


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
        reply_markup = ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True)
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
