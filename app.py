import json
import logging
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, Request

from src import load_config
from src.handlers import register_routes
from src.handlers.keyboards import view_button
from src.middlewares.config import ConfigMiddleware

router = Router()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

config = load_config(".env")

WEBHOOK_PATH = f"/bot/{config.tg.token}"
WEBHOOK_URL = config.tg.webhook_url + WEBHOOK_PATH

storage = MemoryStorage()

bot = Bot(token=config.tg.token,
          default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=storage)


@asynccontextmanager
async def lifespan(app: FastAPI):
    allowed_updates = ['message', 'callback_query']
    await bot.set_webhook(url=WEBHOOK_URL,  allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)

    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan, debug=True)
sentry_sdk.init(
    dsn="https://21e287dc04a89fe04ffbfc7db774bc46@o4507315900383232.ingest.de.sentry.io/4508042355933264",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
# Register middlewares
dp.update.middleware(ConfigMiddleware(config))

# Register routes
register_routes(dp)


@app.post(WEBHOOK_PATH)
async def bot_webhook(request: dict):
    # data = await request.json()
    telegram_update = types.Update(**request)
    # logging.info("Received webhook", request)
    # update = await request.json()
    if telegram_update.callback_query:
        print("callbach", telegram_update.callback_query.data)
    await dp.feed_update(bot=bot, update=telegram_update)


class MyCallback(CallbackData, prefix="my"):
    foo: str
    bar: int


@app.post('/send-message/')
async def bot_webhook(msg: str, user_id: str, order_id: int):

    await bot.send_message(user_id, msg)
    # await state.set_state("dwadaw")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    # uvicorn.run("app:app", host="0.0.0.0", port=8000,reload=True)
