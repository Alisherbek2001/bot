from asyncio import create_task, sleep

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.config import CHANNEL_ID
from src.filters.is_private import IsPrivateFilter
from src.handlers.keyboards import (faktura_document, order_document,
                                    order_document_without_price)
from src.handlers.schemas import FacturaLimitInfo, OrderResponse
from src.handlers.utils import (create_facture, create_facture_without_price,
                                create_full_facture, get_order_as_list)
from src.services import LimitClient, OrderClient

from .keyboards import order_buttons

order_client = OrderClient()
limit_client = LimitClient()
router = Router()
router.message.filter(IsPrivateFilter())
dp = Dispatcher()


@router.message(F.text == order_document)
async def get_document_orders(message: Message, state: FSMContext):
    """
        yuk xati olish
    """
    telegram_id = message.from_user.id
    order_client.get_factura_doc(tg_user_id=telegram_id)


@router.message(F.text == order_document_without_price)
async def get_document_orders_without_price(message: Message, state: FSMContext):
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
            buffer_file = create_facture_without_price(data, price_data)
            await message.answer_document(buffer_file)
    else:
        await message.answer(
            "🙅🏻‍♂️ Sizda faol buyurtmalar yo'q", reply_markup=order_buttons
        )


# ------------------------------------


async def send_faktura(message: Message):
    telegram_id = message.from_user.id
    contracts = limit_client.get_contracts(telegram_id)

    product_response = order_client.get_product_prices(
        tg_user_id=telegram_id)
    price_data = {item['name']: {'price': item['price'],
                                 'measure': item['measure']} for item in product_response}

    i = 0
    for item in contracts:
        i += 1
        await sleep(1)
        jsondata = limit_client.get_factura_data(item.get('id'), telegram_id)
        data = FacturaLimitInfo.model_validate(jsondata)
        dmttname = data.dmtt.name.replace('-', '')
        buf_file = create_full_facture(i, data, price_data)
        await message.bot.send_document(CHANNEL_ID, buf_file,  caption=f"#{dmttname}")


@router.message(F.text == faktura_document)
async def get_document_orders(message: Message):
    """
        faktura yaratish
    """
    create_task(send_faktura(message))
    await message.answer("Yaratish jarayoni boshlandi")
