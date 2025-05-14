import asyncio
import json
import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from src import load_config
from src.handlers import register_routes
from src.handlers.keyboards import view_button
from src.middlewares.config import ConfigMiddleware

router = Router()

logger = logging.getLogger(__name__)

config = load_config(".env")


storage = MemoryStorage()

bot = Bot(token=config.tg.token)
dp = Dispatcher(storage=storage)

# Register middlewares
dp.update.middleware(ConfigMiddleware(config))

# Register routes
register_routes(dp)


async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    asyncio.run(main())
    # uvicorn.run("app:app", host="0.0.0.0", port=8000,reload=True)
