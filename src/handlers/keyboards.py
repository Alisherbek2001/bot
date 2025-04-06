from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

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
        [KeyboardButton(text='✅ Bajarilgan buyurtmalar'),
         KeyboardButton(text='🚫 Rad qilingan buyurtmalar')],
        [KeyboardButton(text=order_document),
         KeyboardButton(text=order_document_without_price)],
        [KeyboardButton(text=faktura_document),],
        [KeyboardButton(text=refresh_db_command),],
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

def get_in_progress_buttons(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Bajarildi",
                    callback_data=f"mark_as_done_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data=f"back_in_progress_orders"
                )
            ]
        ]
    )

COMFIRM_BUTTON_NAME = "Qabul qilish"


def get_confirm_buttons(order_id: int) -> InlineKeyboardMarkup:
    """Active zakazlarni olish uchun"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"confirm_order_{order_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"reject_order_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data=f"back_active_orders"
                )
            ]
        ]
    )
