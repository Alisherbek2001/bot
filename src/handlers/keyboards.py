from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

contact_share_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📞  Telefon raqamni yuborish',
                        request_contact=True)],
    ],
    resize_keyboard=True,
)

view_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='👀 Ko\'rish')],
    ],
    resize_keyboard=True,
)

buttun1 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏛 Firmalarim'),
         KeyboardButton(text='📋 Buyurtmalarim')]
    ],
    resize_keyboard=True,
)

firm_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏛 Mening firmalarim')],
        [KeyboardButton(text='➕ Firma qo\'shish'),
         KeyboardButton(text='❌ Firma o\'chirish')],
        [KeyboardButton(text='⬅️ Orqaga')],
    ],
    resize_keyboard=True,
)

order_document = "📃 Yuk xati"
faktura_document = "📄 Faktura"
order_document_without_price = "📃 Yuk xati(Narxsiz)"
refresh_db_command = "🔄 Bazani yagilash"
order_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🆕 Yangi buyurtmalar'),
         KeyboardButton(text='🚛 Faol buyurtmalar')],

        [KeyboardButton(text=order_document),
         KeyboardButton(text=faktura_document)],


        [KeyboardButton(text='⬅️ Orqaga')],
    ],
    resize_keyboard=True,
)

check_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✅ Ha'), KeyboardButton(text='❌ Yo\'q')]
    ],
    resize_keyboard=True,
)


check_buttons_in_progress = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✅ Bajarildi')],
        [KeyboardButton(text='🔙 Orqaga')],
    ],
    resize_keyboard=True,
)

COMFIRM_BUTTON_NAME = "Qabul qilish"
confirm_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=COMFIRM_BUTTON_NAME),
         KeyboardButton(text='Rad etish')],
        [KeyboardButton(text='🔙 Orqaga')],
    ],
    resize_keyboard=True,
)
