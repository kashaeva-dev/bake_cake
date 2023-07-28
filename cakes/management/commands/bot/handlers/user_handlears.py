import logging.config

from aiogram.dispatcher.filters.state import StatesGroup, State
from asgiref.sync import sync_to_async
from environs import Env

from aiogram import Dispatcher, Bot, types
from aiogram.types import ReplyKeyboardRemove

from cakes.logger_config import logger_config
from cakes.management.commands.bot.keyboards.user_keyboards import (
    get_order_keyword,
    get_just_main_menu_keyboard, get_no_text_keyboard,
)
from cakes.models import (
    Cake,
    Ingredients,
)

logger = logging.getLogger("user_handlers_logger")

logging.config.dictConfig(logger_config)

env = Env()
env.read_env()

bot = Bot(env('TG_BOT_API'), parse_mode=types.ParseMode.HTML)


class OrderFSM(StatesGroup):
    add_text = State()
    add_comment = State()


async def start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Чтобы выбрать 🎂<b>торт</b> перейдите в один из разделов "
                           "каталога по дополнительной кнопке клавиатуры ⬇. ",
                           reply_markup=await get_order_keyword(),
                           )


async def web_app_handler(web_app_message):
    logger.info(f"web_app_data: {web_app_message.web_app_data}")
    chat_id = web_app_message.chat.id
    cake_id = web_app_message.web_app_data.data
    cake = await sync_to_async(Cake.objects.get)(id=cake_id)
    await OrderFSM.add_text.set()
    await bot.send_message(chat_id,
                           f"Вы выбрали торт <b>{cake.name}</b>.\n\n"
                           f"<b>Вес:</b> {cake.weight} кг.\n\n"
                           f"<b>Цена:</b> {cake.current_price} руб.\n\n",
                           reply_markup=ReplyKeyboardRemove(),
                           parse_mode='HTML')
    await bot.send_message(chat_id,
                           "✏ Мы можем разместить на торте любую <b>надпись</b>, "
                           "например:\n\n <b>С днем рождения!</b>\n\n"
                           "Если хотите добавить надпись, пришлите ее текст в ответном сообщении.\n\n"
                           "Стоимость добавления надписи - <b>500 руб.</b>",
                           reply_markup=await get_no_text_keyboard(),
                           parse_mode='HTML')


async def no_text_handler(callback: types.CallbackQuery):
    await OrderFSM.add_comment.set()
    await callback.message.edit_text("📝 Теперь напишите <b>комментарий</b> к заказу, ")


async def choose_standard_cake_handler(web_app_message):
    logger.info(f"web_app_data: {web_app_message.web_app_data}")
    cake_id = web_app_message.web_app_data.data.split('_')[-1]
    cake = await sync_to_async(Cake.objects.get)(id=cake_id)
    chat_id = web_app_message.chat.id
    await bot.send_message(chat_id,
                           f"Вы выбрали торт <b>{cake.name}</b>.\n"
                           f"<b>Вес:</b> {cake.weight} кг.\n"
                           f"<b>Цена:</b> {cake.current_price} руб.\n",
                           reply_markup=ReplyKeyboardRemove(),
                           parse_mode='HTML')
    await bot.send_message(chat_id,
                           f"✏ Мы можем разместить на торте любую <b>надпись</b>, например: 'С днем рождения!'",
                           reply_markup=await get_no_text_keyboard(),
                           parse_mode='HTML')


def register_user_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров для пользователей."""

    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(web_app_handler, content_types='web_app_data')
    # dp.register_message_handler(web_app_handler, lambda web_app_data: web_app_data.web_app_data.data.startswith('cake'))

