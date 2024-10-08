from asyncio import create_task, sleep

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.config import CHANNEL_ID
from src.filters.is_private import IsPrivateFilter
from src.handlers.keyboards import (faktura_document, order_document,
                                    order_document_without_price)
from src.handlers.schemas import FacturaLimitInfo
from src.handlers.utils import create_full_facture
from src.services import LimitClient, OrderClient

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





@router.message(F.text == faktura_document)
async def get_document_orders(message: Message):
    """
        faktura yaratish
    """
    await message.answer("Yaratish jarayoni boshlandi")
    return order_client.get_full_factura_doc(message.from_user.id)
