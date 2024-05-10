import logging
from contextlib import asynccontextmanager
from src.handlers.keyboards import view_button
import uvicorn
from aiogram.types import Message,CallbackQuery
from aiogram import types, Router, Dispatcher,F

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.callback_data import CallbackData
from src import load_config
from src.handlers import register_routes
from src.middlewares.config import ConfigMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()
from aiogram.fsm.context import FSMContext
logger = logging.getLogger(__name__)

config = load_config(".env")


storage = MemoryStorage()

bot = Bot(token=config.tg.token, parse_mode="HTML")
dp = Dispatcher(storage=storage)

# Register middlewares
dp.update.middleware(ConfigMiddleware(config))

# Register routes
register_routes(dp)

import json

async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)
    

import asyncio 

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    asyncio.run(main())
    # uvicorn.run("app:app", host="0.0.0.0", port=8000,reload=True)
