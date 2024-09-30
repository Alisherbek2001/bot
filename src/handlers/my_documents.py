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
    return order_client.get_factura_doc(tg_user_id=telegram_id)


@router.message(F.text == order_document_without_price)
async def get_document_orders_without_price(message: Message, state: FSMContext):
    """
        yuk xati olish narxsiz
    """
    telegram_id = message.from_user.id
    return order_client.get_factura_doc_without_price(
        tg_user_id=telegram_id)


# ------------------------------------


async def send_faktura(message: Message):
    telegram_id = message.from_user.id
    # telegram_id = 6996405082
    contracts = limit_client.get_contracts(telegram_id)

    price_data = order_client.get_product_prices(
        tg_user_id=telegram_id)

    i = 0
    count = len(contracts)
    for item in contracts:
        i += 1
        jsondata = limit_client.get_factura_data(item.get('id'), telegram_id)
        data = FacturaLimitInfo.model_validate(jsondata)
        dmttname = data.dmtt.name.replace('-', '')
        buf_file = create_full_facture(i, data, price_data)
        await message.bot.send_document(CHANNEL_ID, buf_file,  caption=f"#{dmttname}\n{i}/{count}")


@router.message(F.text == faktura_document)
async def get_document_orders(message: Message):
    """
        faktura yaratish
    """
    await message.answer("Yaratish jarayoni boshlandi")
    return await send_faktura(message) 
