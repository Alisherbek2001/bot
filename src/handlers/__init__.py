from aiogram import Dispatcher

from .my_company import router as company_router
from .my_order import router as order_router
from .start import router as start_routes


def register_routes(dp: Dispatcher):
    dp.include_router(start_routes)
    dp.include_router(order_router)
    dp.include_router(company_router)
