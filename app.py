import logging
from contextlib import asynccontextmanager
from src.handlers.keyboards import view_button
import uvicorn
from aiogram.types import Message,CallbackQuery
from aiogram import types, Router, Dispatcher,F
from fastapi import FastAPI
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
from fastapi import Request
config = load_config(".env")

WEBHOOK_PATH = f"/bot/{config.tg.token}"
WEBHOOK_URL = config.tg.webhook_url + WEBHOOK_PATH

storage = MemoryStorage()

bot = Bot(token=config.tg.token, parse_mode="HTML")
dp = Dispatcher(storage=storage)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=WEBHOOK_URL)

    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)

# Register middlewares
dp.update.middleware(ConfigMiddleware(config))

# Register routes
register_routes(dp)

import json

@app.post(WEBHOOK_PATH)
async def bot_webhook(req:Request):
    print(await req.body())
    update = await req.json()
    telegram_update = types.Update(**update)    
    await dp.feed_webhook_update(bot=bot, update=telegram_update)


class MyCallback(CallbackData, prefix="my"):
    foo: str
    bar: int

@app.post('/send-message/')
async def bot_webhook(msg: str,user_id:str,order_id:int):
    builder = InlineKeyboardBuilder()
    builder.button(
    text="Ko'rish",
    callback_data=MyCallback(foo="demo", bar=f"{order_id}")  # Value can be not packed to string inplace, because builder knows what to do with callback instance
)   
    await bot.send_message(user_id,msg,reply_markup=builder.as_markup())
    # await state.set_state("dwadaw")





if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    # uvicorn.run("app:app", host="0.0.0.0", port=8000,reload=True)
