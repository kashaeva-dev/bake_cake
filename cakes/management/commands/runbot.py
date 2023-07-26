import logging.config

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from django.core.management import BaseCommand

import conf.settings as settings
from cakes.logger_config import logger_config

logger = logging.getLogger("bot_logger")

logging.config.dictConfig(logger_config)

storage = MemoryStorage()
bot = Bot(token=settings.TG_BOT_API, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

web_app = WebAppInfo(url="https://kashaeva-dev.github.io/")

keyword = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍰 Стандартные торты", web_app=web_app)],
        [KeyboardButton(text="🛒 Из моих заказов", web_app=web_app)],
    ],
    resize_keyboard=True,
)

inline_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
    ],
]
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Чтобы выбрать 🎂<b>торт</b> перейдите в один из разделов "
                           "каталога по дополнительной кнопке клавиатуры ⬇. ",
                           reply_markup=keyword,
                           )


@dp.message_handler(content_types='web_app_data')
async def web_app_handler(web_app_message):
    logger.info(f"web_app_data: {web_app_message.web_app_data}")
    chat_id = web_app_message.chat.id
    await bot.send_message(chat_id,
                           f"Выбран торт №{web_app_message.web_app_data.data}. ",
                           reply_markup=ReplyKeyboardRemove())
    await bot.send_message(chat_id,
                           f"Чтобы продолжить оформление заказа, выберите один из пунктов меню:",
                           reply_markup=inline_keyboard)

class Command(BaseCommand):
    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
