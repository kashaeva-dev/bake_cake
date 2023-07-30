import calendar
import datetime
import logging
import logging.config
import os

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from asgiref.sync import sync_to_async
from django.utils import timezone
from environs import Env

from aiogram import Dispatcher, Bot, types
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from cakes.logger_config import logger_config
from cakes.management.commands.bot.keyboards.user_keyboards import (
    get_order_keyword,
    get_just_main_menu_keyboard,
    get_no_text_keyboard,
    get_no_comment_keyboard,
    get_month_keyboard, get_delivery_type_keyboard, get_delivery_time_keyboard, get_conformation_keyboard,
)
from cakes.models import (
    Cake,
    Ingredients, DeliveryType, Client, Order, OrderStatus, DeliveryTime,
)
from conf.settings import BASE_DIR

logger = logging.getLogger("user_handlers_logger")

logging.config.dictConfig(logger_config)

env = Env()
env.read_env()

bot = Bot(env('TG_BOT_API'), parse_mode=types.ParseMode.HTML)


class OrderFSM(StatesGroup):
    web_app = State()
    add_text = State()
    add_comment = State()
    choose_delivery_type = State()
    choose_delivery_date = State()
    choose_delivery_time = State()
    get_delivery_address = State()
    get_delivery_comment = State()
    get_phone_number = State()
    get_contact_name = State()
    conformation = State()


async def start(message: types.Message):
    logger.info(f"message: {message.from_user.id}")
    await OrderFSM.web_app.set()
    await bot.send_message(message.from_user.id,
                           "Чтобы выбрать 🎂<b>торт</b> перейдите в один из разделов "
                           "каталога по дополнительной кнопке клавиатуры ⬇. ",
                           reply_markup=await get_order_keyword(),
                           )


async def web_app_data_handler(web_app_message, state: FSMContext):
    logger.info(f"web_app_data: {web_app_message.web_app_data}")
    chat_id = web_app_message.chat.id
    case, item_id = web_app_message.web_app_data.data.split('_')
    match case:
        case 'cake':
            cake = await sync_to_async(Cake.objects.get)(id=item_id)
            async with state.proxy() as data:
                data['cake'] = cake
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


add_comment_text = "💬 Если хотите, Вы можете написать "\
                   "<b>комментарий к заказу</b> в ответном сообщении."

async def add_text_handler(message: types.Message, state: FSMContext):
    logger.info(f"add_text_handler: {message.text}")
    async with state.proxy() as data:
        data['text'] = message.text
    await OrderFSM.add_comment.set()
    await message.answer(add_comment_text,
                         reply_markup=await get_no_comment_keyboard(),
                         parse_mode='HTML',
                         )


async def no_text_handler(callback: types.CallbackQuery, state: FSMContext):
    await OrderFSM.add_comment.set()
    async with state.proxy() as data:
        data['text'] = 'без надписи'
    await callback.message.edit_text(add_comment_text,
                                     reply_markup=await get_no_comment_keyboard(),
                                     parse_mode='HTML',
                                     )


async def add_comment_handler(message: types.Message, state: FSMContext):
    logger.info(f"add_comment_handler: {message.text}")
    async with state.proxy() as data:
        data['comment'] = message.text
    await OrderFSM.choose_delivery_type.set()
    await message.answer("🚚 Выберите <b>способ доставки</b>:",
                         reply_markup=await get_delivery_type_keyboard(),
                         parse_mode='HTML',
                         )


async def no_comment_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"no_comment_handler: {callback.data}")
    await OrderFSM.choose_delivery_type.set()
    async with state.proxy() as data:
        data['comment'] = 'без комментария'
    logger.info(f'no comment sending message')
    await callback.message.edit_text("🚚 Пожалуйста, выберите <b>способ доставки</b>:",
                                     reply_markup=await get_delivery_type_keyboard(),
                                     parse_mode='HTML',
                                     )


choose_delivery_date_text = "📅 Выберите <b>дату доставки</b>:\n\n"\
                            "⚡ Доставка в ближайшие 24 часа <b>увеличивает стоимость заказа на 20%.</b>"


async def choose_delivery_type_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"choose_delivery_type_handler: {callback.data}")
    delivery_type_id = callback.data.split('_')[-1]
    delivery_type = await sync_to_async(DeliveryType.objects.get)(id=delivery_type_id)
    async with state.proxy() as data:
        data['delivery_type'] = delivery_type
    await OrderFSM.choose_delivery_date.set()
    year = datetime.date.today().year
    month = datetime.date.today().month
    await callback.message.edit_text(choose_delivery_date_text,
                                     reply_markup=await get_month_keyboard(month, year),
                                     parse_mode='HTML',
                                     )


async def next_month_handler(callback: types.CallbackQuery):
    month, year = callback.data.split('_')[-2:]
    logger.info(f'next_month_handler {month} {year}')
    next_month = (int(month) + 1) % 12
    next_month_year = int(year) + (int(month) + 1) // 12
    logger.info(f'calendar next month {next_month_year} {next_month}')
    await callback.message.edit_text(choose_delivery_date_text,
                                     reply_markup=await get_month_keyboard(next_month, next_month_year)
                                     )


async def prev_month_handler(callback: types.CallbackQuery):
    month, year = callback.data.split('_')[-2:]
    prev_month = (int(month) + 11) % 12
    prev_month_year = int(year) - ((int(month) + 11) // 12 - 1)
    await callback.message.edit_text(choose_delivery_date_text,
                                     reply_markup=await get_month_keyboard(prev_month, prev_month_year)
                                     )


async def choose_delivery_date_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"choose_delivery_date_handler: {callback.data}")
    day, month, year = callback.data.split('_')[-3:]
    delivery_date = datetime.date(int(year), int(month), int(day))
    logger.info(f"delivery_date_choosen: {delivery_date}")
    async with state.proxy() as data:
        data['delivery_date'] = delivery_date
        delivery_type = data['delivery_type']
    if delivery_type.id == 1:
        pass
    else:
        await OrderFSM.choose_delivery_time.set()
        await callback.message.edit_text("🕒 Выберите <b>время доставки</b>:\n\n"
                                         "⚡ Доставка в ближайшие 24 часа <b>увеличивает стоимость заказа на 20%.</b>",
                                         reply_markup=await get_delivery_time_keyboard(),
                                         parse_mode='HTML',
                                         )

async def choose_delivery_time_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"choose_delivery_time_handler: {callback.data}")
    delivery_hour = callback.data.split('_')[-1]
    async with state.proxy() as data:
        data['delivery_time'] = datetime.time(int(delivery_hour), 0)
    await OrderFSM.get_delivery_address.set()
    await callback.message.edit_text("🏠 Пожалуйста, <b>укажите адрес доставки</b> в ответном сообщении:\n\n"
                                     "📌 <i>Например: г. Москва, ул. Ленина, д. 1, кв. 1</i>",
                                     reply_markup=await get_just_main_menu_keyboard(),
                                     parse_mode='HTML',
                                     )

async def get_delivery_address_handler(message: types.Message, state: FSMContext):
    logger.info(f"get_delivery_address_handler: {message.text}")
    async with state.proxy() as data:
        data['delivery_address'] = message.text
    await OrderFSM.get_delivery_comment.set()
    await message.answer("💬 Если необходимо, укажите <b>комментарий для курьера</b> в ответном сообщении:\n\n"
                         "📌 <i>Например: звонить за 30 минут до приезда</i>",
                         reply_markup=await get_no_comment_keyboard(),
                         parse_mode='HTML',
                         )


async def no_delivery_comment_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"no_delivery_comment_handler: {callback.data}")
    async with state.proxy() as data:
        data['delivery_comment'] = ''
    await OrderFSM.get_phone_number.set()
    await callback.message.edit_text("📞 Пожалуйста, <b>укажите номер телефона</b> в ответном сообщении:\n\n"
                                     "📌 <i>Например: +7 (999) 999-99-99</i>",
                                     reply_markup=await get_just_main_menu_keyboard(),
                                     parse_mode='HTML',
                                     )


async def get_delivery_comment_handler(message: types.Message, state: FSMContext):
    logger.info(f"get_delivery_comment_handler: {message.text}")
    async with state.proxy() as data:
        data['delivery_comment'] = message.text
    await OrderFSM.get_phone_number.set()
    await message.answer("📞 Пожалуйста, <b>укажите номер телефона</b> в ответном сообщении:\n\n"
                         "📌 <i>Например: +7 (999) 999-99-99</i>",
                         reply_markup=await get_just_main_menu_keyboard(),
                         parse_mode='HTML',
                         )


async def get_phone_number_handler(message: types.Message, state: FSMContext):
    logger.info(f"get_phone_number_handler: {message.text}")
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await OrderFSM.get_contact_name.set()
    await message.answer("👤 Пожалуйста, <b>укажите имя контактного лица</b> в ответном сообщении:\n\n",
                         reply_markup=await get_just_main_menu_keyboard(),
                         parse_mode='HTML',
                         )


async def get_contact_name_handler(message: types.Message, state: FSMContext):
    logger.info(f"get_contact_name_handler: {message.text}")
    async with state.proxy() as data:
        data['contact_name'] = message.text
        cake = data['cake']
        cake_text = data['text']
        if cake_text == "без надписи":
            text_price = 0
        else:
            text_price = 500
        total_cake_price = cake.current_price + text_price
        cake_comment = data['comment']
        delivery_type = data['delivery_type']
        delivery_date = data['delivery_date']
        logger.info(f'{delivery_date}')
        delivery_start_time = data['delivery_time'].strftime("%H:%M")
        logger.info(f'{delivery_start_time}')
        delivery_end_time = datetime.time((data['delivery_time'].hour + 2), 0).strftime("%H:%M")
        logger.info(f'{delivery_start_time} - {delivery_end_time}')
        delivery_address = data['delivery_address']
        delivery_comment = data['delivery_comment']
        phone_number = data['phone_number']
        contact_name = data['contact_name']
        data['total_cake_price'] = total_cake_price
    delivery_price = delivery_type.current_price
    logger.info(f'total_cake_price: {total_cake_price}')
    await OrderFSM.conformation.set()
    logger.info({BASE_DIR})
    picture_path = os.path.join(BASE_DIR, cake.picture.url.lstrip('/'))
    logger.info(f'picture path {picture_path}')
    picture = InputFile(picture_path)
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f"Вы собираетеcь заказать торт 🎂 <b>{cake.name}</b>\n\n",
                         photo=picture,
                         )
    await message.answer("📝 Пожалуйста, проверьте правильность введенных данных:\n\n"
                         f"🎂 <b>Торт:</b> {cake.name}\n\n"
                         f"📝 <b>Надпись:</b> {cake_text}\n\n"
                         f"💬 <b>Комментарий к торту:</b> {cake_comment}\n\n"
                         f"🚚 <b>Способ доставки:</b> {delivery_type}\n\n"
                         f"📅 <b>Дата доставки:</b> {delivery_date}\n\n"
                         f"🕒 <b>Время доставки:</b> {delivery_start_time} - {delivery_end_time}\n\n"
                         f"🏠 <b>Адрес доставки:</b> {delivery_address}\n\n"
                         f"💬 <b>Комментарий для курьера:</b> {delivery_comment}\n\n"
                         f"📞 <b>Номер телефона:</b> {phone_number}\n\n"
                         f"👤 <b>Имя контактного лица:</b> {contact_name}\n\n"
                         f"💰 <b>Итоговая стоимость торта c доставкой:</b> {total_cake_price + delivery_price}\n\n",
                         reply_markup=await get_conformation_keyboard(),
                         parse_mode='HTML',
                         )


async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.from_user.id
    client = await sync_to_async(Client.objects.get)(chat_id=chat_id)
    status = await sync_to_async(OrderStatus.objects.get)(pk=1)
    try:
        async with state.proxy() as data:
            order = await sync_to_async(Order.objects.create)(
                client=client,
                cake=data['cake'],
                text=data['text'],
                cake_comment=data['comment'],
                status=status,
                total_cake_price=data['total_cake_price'],
                delivery_type=data['delivery_type'],
                total_delivery_price=data['delivery_type'].current_price,
                delivery_address=data['delivery_address'],
                delivery_comment=data['delivery_comment'],
                contact_phone=data['phone_number'],
                contact_name=data['contact_name']
                )
            moscow_tz = pytz.timezone('Europe/Moscow')
            if data['delivery_type'].pk == 1:
                delivery_time = await sync_to_async(DeliveryTime.objects.create)(
                    order=order,
                    delivery_date=timezone.make_aware(data['delivery_date'], moscow_tz),
                    delivery_status='initial',
                )
            else:
                delivery_time = await sync_to_async(DeliveryTime.objects.create)(
                    order=order,
                    delivery_date=timezone.make_aware(data['delivery_date'], moscow_tz),
                    delivery_time=timezone.make_aware(data['delivery_time'], moscow_tz),
                    delivery_status='initial',
                )
    except:
        logger.info(f'Ошибка записи в базу данных, data: {data}')
    else:
        await callback.message.answer(
            f"Ваш заказ <b>№{ order.pk }</b> успешно создан!",
            reply_markup=await get_just_main_menu_keyboard(),
            parse_mode='HTML',
        )


def register_user_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров для пользователей."""

    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(web_app_data_handler, content_types='web_app_data', state='*')
    dp.register_callback_query_handler(no_text_handler,
                                       lambda callback_query: callback_query.data == 'no_text', state='*')
    dp.register_message_handler(add_text_handler, state=OrderFSM.add_text)
    dp.register_callback_query_handler(no_comment_handler,
                                       lambda callback_query: callback_query.data == 'no_comment',
                                       state=OrderFSM.add_comment)
    dp.register_callback_query_handler(no_delivery_comment_handler,
                                       lambda callback_query: callback_query.data == 'no_comment',
                                       state=OrderFSM.get_delivery_comment)
    dp.register_message_handler(add_comment_handler, state=OrderFSM.add_comment)
    dp.register_callback_query_handler(prev_month_handler,
                                       lambda callback_query: callback_query.data.startswith('prev_month_'),
                                       state=OrderFSM.choose_delivery_date)
    dp.register_callback_query_handler(next_month_handler,
                                       lambda callback_query: callback_query.data.startswith('next_month_'),
                                       state=OrderFSM.choose_delivery_date)
    dp.register_callback_query_handler(choose_delivery_type_handler,
                                       lambda callback_query: callback_query.data.startswith('delivery_type_'),
                                       state=OrderFSM.choose_delivery_type)
    dp.register_callback_query_handler(choose_delivery_date_handler,
                                       lambda callback_query: callback_query.data.startswith('delivery_date_'),
                                       state=OrderFSM.choose_delivery_date)
    dp.register_callback_query_handler(choose_delivery_time_handler,
                                        lambda callback_query: callback_query.data.startswith('delivery_time_'),
                                        state=OrderFSM.choose_delivery_time)
    dp.register_message_handler(get_delivery_address_handler, state=OrderFSM.get_delivery_address)
    dp.register_message_handler(get_delivery_comment_handler, state=OrderFSM.get_delivery_comment)
    dp.register_message_handler(get_phone_number_handler, state=OrderFSM.get_phone_number)
    dp.register_message_handler(get_contact_name_handler, state=OrderFSM.get_contact_name)
    dp.register_callback_query_handler(confirm_order,
                                       lambda callback_query: callback_query.data == 'confirm_order',
                                       state=OrderFSM.conformation,
                                       )



if __name__ == "__main__":
    print(datetime.date(2023, 7, 31))
