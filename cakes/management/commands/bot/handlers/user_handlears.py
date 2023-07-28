import logging.config
from environs import Env

from aiogram import Dispatcher, Bot, types
from aiogram.types import ReplyKeyboardRemove

from cakes.logger_config import logger_config
from cakes.management.commands.bot.keyboards.user_keyboards import (
    order_keyword,
    main_menu_iKeyboard,
)

logger = logging.getLogger("user_handlers_logger")

logging.config.dictConfig(logger_config)

env = Env()
env.read_env()

bot = Bot(env('TG_BOT_API'), parse_mode=types.ParseMode.HTML)


async def start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Чтобы выбрать 🎂<b>торт</b> перейдите в один из разделов "
                           "каталога по дополнительной кнопке клавиатуры ⬇. ",
                           reply_markup=order_keyword,
                           )


async def web_app_handler(web_app_message):
    logger.info(f"web_app_data: {web_app_message.web_app_data}")
    chat_id = web_app_message.chat.id
    await bot.send_message(chat_id,
                           f"Выбран торт №{web_app_message.web_app_data.data}. ",
                           reply_markup=ReplyKeyboardRemove())
    await bot.send_message(chat_id,
                           f"Чтобы продолжить оформление заказа, выберите один из пунктов меню:",
                           reply_markup=main_menu_iKeyboard)


def register_user_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров для пользователей."""

    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(web_app_handler, content_types='web_app_data')
