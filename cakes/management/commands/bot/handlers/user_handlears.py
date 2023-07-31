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
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, InputFile, ParseMode

from cakes.logger_config import logger_config
from cakes.management.commands.bot.keyboards.user_keyboards import (
    get_order_keyboard,
    get_just_main_menu_keyboard,
    get_no_text_keyboard,
    get_no_comment_keyboard,
    get_month_keyboard,
    get_delivery_type_keyboard,
    get_delivery_time_keyboard,
    get_conformation_keyboard,
    get_choosing_order_from_keyboard,
    get_choose_topping_keyboard,
    get_choose_berry_keyboard, get_choose_decor_keyboard, get_choose_level_keyboard, get_choose_form_keyboard,
    get_main_menu_keyboard, get_my_orders_keyboard,
)
from cakes.models import (
    Cake,
    Ingredients, DeliveryType, Client, Order, OrderStatus, DeliveryTime, Form, Level,
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


class CreateCakeFSM(StatesGroup):
    choose_level = State()
    choose_form = State()
    add_topping = State()
    add_berries = State()
    add_decor = State()

async def start(message: types.Message):
    logger.info(f"message: {message.from_user.id}")
    await bot.send_message(message.from_user.id,
                           '🤖 ГЛАВНОЕ МЕНЮ:',
                           parse_mode='HTML',
                           reply_markup=await get_main_menu_keyboard(),
                           )


async def get_main_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"Main menu handler")
    await state.finish()
    if state in [OrderFSM.web_app,
                 OrderFSM.add_text,
                 OrderFSM.add_comment,
                 OrderFSM.choose_delivery_type,
                 OrderFSM.choose_delivery_date,
                 OrderFSM.choose_delivery_time,
                 OrderFSM.get_delivery_address,
                 OrderFSM.get_delivery_comment,
                 OrderFSM.get_phone_number,
                 OrderFSM.get_contact_name,
                 OrderFSM.conformation,
                 CreateCakeFSM.choose_level,
                 CreateCakeFSM.choose_form,
                 CreateCakeFSM.add_topping,
                 CreateCakeFSM.add_berries,
                 CreateCakeFSM.add_decor,
                 ]:
        await bot.send_message(callback.from_user.id,
                           text='Вернулись к главному меню, все промежуточные данные очищены',
                           reply_markup=ReplyKeyboardRemove())
    await callback.message.edit_text('🤖 ГЛАВНОЕ МЕНЮ:',
                                     parse_mode='HTML',
                                     reply_markup=await get_main_menu_keyboard(),
                                     )


async def start_order_handler(callback: types.CallbackQuery):
    logger.info(f"Start order handler")
    await callback.message.edit_text("Пожалуйста, выберите один из пунктов меню:",
                                     reply_markup=await get_choosing_order_from_keyboard(),
                                     )


async def FAQ_handler(callback: types.CallbackQuery):
    logger.info(f"Start FAQ handler")
    await callback.message.edit_text("Мы - семейная пекарня BakeCake!\n\n"
                                     "Наша миссия - сделать так, чтобы Вы наслаждались вкусом!\n\n"
                                     "Стоимость наших тортов зависит от начинки и составляет от "
                                     "1000 руб. до 1800 руб. за 1 кг. торта.\n\n"
                                     "У нас Вы можете заказать как стандартный торт из "
                                     "каталога, так и собрать в конструкторе свой собственный торт, а "
                                     "мы испечем и доставим его Вам.\n\n"
                                     "🚚 Доставка возможна не ранее, чем на следующий день, при этом"
                                     " если время между заказом и доставкой составляем менее 24 часов, "
                                     "то стоимость торта увеличивается на 20%.\n\n"
                                     "🏠 Вы также можете забрать готовый торт самостоятельно,\n"
                                     "мы находимся по адресу: <b>Москва, м. Пражская, ул. Сосновая, д.45.</b>\n\n"
                                     "📞 Наш телефон: +7 (495) 456-56-56.\n\n"
                                     "Мы всегда Вам рады!",
                                     reply_markup=await get_just_main_menu_keyboard(),
                                     parse_mode='HTML',
                                     )


async def start_choose_cake_handler(callback: types.CallbackQuery):
    logger.info('Start choose cake handler')
    await OrderFSM.web_app.set()
    await bot.send_message(callback.from_user.id,
                           "Чтобы выбрать 🎂<b>торт</b> перейдите в один из разделов "
                           "каталога по дополнительной кнопке клавиатуры ⬇. ",
                           reply_markup=await get_order_keyboard(),
                           parse_mode='HTML',
                           )


async def start_create_cake_handler(callback: types.CallbackQuery):
    logger.info("Start create cake handler")
    await CreateCakeFSM.choose_level.set()
    await bot.send_message(callback.from_user.id,
                           "Вначале нужно выбрать <b>количество уровней.</b>\n\n",
                           reply_markup=await get_choose_level_keyboard(),
                           parse_mode='HTML',
                           )


async def choose_level_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info('Choose level handler')
    level_id = callback.data.split('_')[-1]
    level = await sync_to_async(Level.objects.get)(id=level_id)
    await CreateCakeFSM.choose_form.set()
    async with state.proxy() as data:
        data['level'] = level
        data['total_cake_price'] = level.current_price
    await callback.message.edit_text(f"Вы выбрали <b>количество уровней</b>: {level.quantity}\n\n"
                                     f"Общая стоимость: {level.current_price} руб.\n\n"
                                     "Теперь выберите <b>форму</b> торта. ",
                                     reply_markup=await get_choose_form_keyboard(),
                                     parse_mode='HTML',
                                     )


async def choose_form_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info('Choose form handler')
    form_id = callback.data.split('_')[-1]
    form = await sync_to_async(Form.objects.get)(id=form_id)
    await CreateCakeFSM.add_topping.set()
    async with state.proxy() as data:
        data['form'] = form
        data['total_cake_price'] += form.current_price
        cake, created = await sync_to_async(Cake.objects.get_or_create)(form=form,
                                                                  level=data['level'],
                                                                  name='Заказной',
                                                                  defaults={
                                                                      'current_price': data['total_cake_price'],
                                                                      'standard': False,
                                                                  })
        logger.info(f"cake: {cake.name} {created}")
        if not created:
            cake.current_price = int(data['total_cake_price'])
            await sync_to_async(cake.save)()
            logger.info(f"Price was changed to {cake.current_price}")
        data['cake'] = cake
        data['standard'] = cake.standard
        total_cake_price = data['total_cake_price']
    logger.info(f"total_cake_price: {total_cake_price}")
    await bot.send_message(callback.from_user.id,
                           f"Вы выбрали форму: <b>{form.name}</b>\n\n"
                           f"Общая стоимость: <b>{total_cake_price}</b> руб.\n\n"
                           "Теперь нужно выбрать <b>топпинг.</b>\n\n"
                           "Перейдите в каталог по дополнительной кнопке клавиатуры ⬇ "
                           "и <b>выберите один</b> из возможных топпингов. ",
                           reply_markup=await get_choose_topping_keyboard(),
                           parse_mode='HTML',
                           )


async def no_berries_handler(message: types.Message, state: FSMContext):
    logger.info('No berries handler')
    await CreateCakeFSM.add_decor.set()
    async with state.proxy() as data:
        data['berry'] = ""
        total_cake_price = data['total_cake_price']
    await bot.send_message(message.from_user.id,
                           "Торт будет без ягод.\n\n"
                           f"Общая стоимость: <b>{total_cake_price}</b> руб.\n\n"
                           "Теперь выберите <b>декор</b> для торта. ",
                           reply_markup=await get_choose_decor_keyboard(),
                           parse_mode='HTML',
                           )


async def no_decoration_handler(message: types.Message, state: FSMContext):
    logger.info('No decoration handler')
    await CreateCakeFSM.add_decor.set()
    async with state.proxy() as data:
        data['decoration'] = ""
        total_cake_price = data['total_cake_price']
    await bot.send_message(message.from_user.id,
                            "Торт будет без декора.\n\n"
                            f"Общая стоимость: <b>{total_cake_price}</b> руб.\n\n",
                            reply_markup=ReplyKeyboardRemove(),
                            parse_mode='HTML',
                            )
    await bot.send_message(message.from_user.id,
                           "✏ Мы можем разместить на торте любую <b>надпись</b>, "
                           "например:\n\n <b>С днем рождения!</b>\n\n"
                           "Если хотите добавить надпись, пришлите ее текст в ответном сообщении.\n\n"
                           "Стоимость добавления надписи - <b>500 руб.</b>",
                           reply_markup=await get_no_text_keyboard(),
                           parse_mode='HTML'
                           )


async def web_app_data_handler(web_app_message, state: FSMContext):
    logger.info(f"web_app_data: {web_app_message.web_app_data}")
    chat_id = web_app_message.chat.id
    case, item_id = web_app_message.web_app_data.data.split('_')
    match case:
        case 'cake':
            cake = await sync_to_async(Cake.objects.get)(id=item_id)
            async with state.proxy() as data:
                data['standard'] = cake.standard
                data['total_cake_price'] = cake.current_price
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
        case 'topping':
            topping = await sync_to_async(Ingredients.objects.get)(id=item_id)
            async with state.proxy() as data:
                data['topping'] = topping
                data['total_cake_price'] += topping.current_price
                total_cake_price = data['total_cake_price']
            await CreateCakeFSM.add_berries.set()
            await bot.send_message(chat_id,
                                   f"Вы выбрали топпинг: <b>{topping.name}</b>.\n\n"
                                   f"Общая стоимость: <b>{total_cake_price}</b> руб.\n\n"
                                   "Теперь можно выбрать ягоды, для этого, перейдите в "
                                   "каталог по дополнительной кнопке клавиатуры ⬇ и выберите одну из возможных ягод.",
                                   reply_markup=await get_choose_berry_keyboard(),
                                   parse_mode='HTML')
        case 'berry':
            berry = await sync_to_async(Ingredients.objects.get)(id=item_id)
            async with state.proxy() as data:
                data['berry'] = berry
                data['total_cake_price'] += berry.current_price
                total_cake_price = data['total_cake_price']
            await CreateCakeFSM.add_decor.set()
            await bot.send_message(chat_id,
                                   f"Вы выбрали ягоду <b>{berry.name}</b>.\n\n"
                                   f"Общая стоимость: <b>{total_cake_price}</b> руб.\n\n"
                                   "Теперь можно выбрать декор, для этого, перейдите в "
                                   "каталог по дополнительной кнопке клавиатуры ⬇ и выберите один из возможных декоров.",
                                   reply_markup=await get_choose_decor_keyboard(),
                                   parse_mode='HTML',
                                   )
        case 'decoration':
            decoration = await sync_to_async(Ingredients.objects.get)(id=item_id)

            async with state.proxy() as data:
                data['decoration'] = decoration
                data['total_cake_price'] += decoration.current_price
                total_cake_price = data['total_cake_price']
            await OrderFSM.add_text.set()
            await bot.send_message(chat_id,
                                   f"Вы выбрали декор <b>{decoration.name}</b>.\n\n"
                                   f"Общая стоимость: <b>{total_cake_price}</b> руб.\n\n",
                                   reply_markup=ReplyKeyboardRemove(),
                                   parse_mode='HTML',
                                   )
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


get_phone_number_text = "📞 Пожалуйста, *укажите номер телефона* в ответном сообщении:\n\n"\
                         "📌 Например: +7 (999) 999-99-99\n\n"\
                         f"Продолжая, Вы даете свое [согласие на обработку персональных данных]"\
                         f"(https://docs.google.com/document/"\
                         f"d/1U-ZZa9bosHbqEbVwvgubUdR6T9gC33igDmEUMYVREQw/edit?usp=sharing).\n\n"


async def choose_delivery_date_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"choose_delivery_date_handler: {callback.data}")
    day, month, year = callback.data.split('_')[-3:]
    delivery_date = datetime.date(int(year), int(month), int(day))
    logger.info(f"delivery_date_choosen: {delivery_date}")
    async with state.proxy() as data:
        data['delivery_date'] = delivery_date
        delivery_type = data['delivery_type']
    if delivery_type.id == 1:
        async with state.proxy() as data:
            data['delivery_address'] = ''
            data['delivery_comment'] = ''
        await OrderFSM.get_phone_number.set()
        await callback.message.edit_text(get_phone_number_text,
                                         reply_markup=await get_just_main_menu_keyboard(),
                                         parse_mode=ParseMode.MARKDOWN,
                                         disable_web_page_preview=True,
                                         )
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
    current_hour = datetime.datetime.now().hour
    current_date = datetime.date.today()
    tomorrow = current_date + datetime.timedelta(days=1)
    logger.info(f"tomorrow: {tomorrow}")
    await OrderFSM.get_delivery_address.set()
    async with state.proxy() as data:
        delivery_date = data['delivery_date']
        is_urgent = tomorrow == delivery_date and int(delivery_hour) < int(current_hour)
        logger.info(f"is_urgent: {is_urgent}")
        data['delivery_time'] = datetime.time(int(delivery_hour), 0)
        logger.info(f"delivery_time: {data['delivery_time']}")
        if is_urgent:
            logger.info(f"total_cake_price: {data['total_cake_price']}")
            data['total_cake_price'] = int(int(data['total_cake_price']) * 1.2)
        total_cake_price = data['total_cake_price']
        logger.info(f"total_cake_price: {total_cake_price}")
    if is_urgent:
        await callback.message.answer("⚠️ <b>Срок доставки составляет менее 24-х часов,"
                                          " стоимость торта будет увеличена на 20%.</b>\n\n"
                                          f"Общая стоимость торта составит {total_cake_price} руб.\n\n"
                                          "🏠 Пожалуйста, <b>укажите адрес доставки</b> в ответном сообщении:\n\n"
                                          "📌 <i>Например: г. Москва, ул. Ленина, д. 1, кв. 1</i>",
                                          reply_markup=await get_just_main_menu_keyboard(),
                                          parse_mode='HTML',
                                          )
    else:
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
    await callback.message.edit_text(get_phone_number_text,
                                     reply_markup=await get_just_main_menu_keyboard(),
                                     parse_mode=ParseMode.MARKDOWN,
                                     disable_web_page_preview=True,
                                     )


async def get_delivery_comment_handler(message: types.Message, state: FSMContext):
    logger.info(f"get_delivery_comment_handler: {message.text}")
    async with state.proxy() as data:
        data['delivery_comment'] = message.text
    await OrderFSM.get_phone_number.set()
    await message.answer(get_phone_number_text,
                         reply_markup=await get_just_main_menu_keyboard(),
                         parse_mode=ParseMode.MARKDOWN,
                         disable_web_page_preview=True,
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
        data['total_cake_price'] += text_price
        total_cake_price = data['total_cake_price']
        cake_comment = data['comment']
        delivery_type = data['delivery_type']
        delivery_date = data['delivery_date']
        logger.info(f'{delivery_date}')
        if delivery_type.pk != 1:
            delivery_start_time = data['delivery_time'].strftime("%H:%M")
            logger.info(f'{delivery_start_time}')
            delivery_end_time = datetime.time((data['delivery_time'].hour + 2), 0).strftime("%H:%M")
            logger.info(f'{delivery_start_time} - {delivery_end_time}')
            delivery_address = data['delivery_address']
            delivery_comment = data['delivery_comment']
        phone_number = data['phone_number']
        contact_name = data['contact_name']
        standard = data['standard']
        logger.info(f'standard: {standard}')
        if not standard:
            level = data['level']
            form = data['form']
            topping = data['topping']
            berry = data['berry']
            decoration = data['decoration']
            logger.info({decoration})
    delivery_price = delivery_type.current_price
    logger.info(f'total_cake_price: {total_cake_price}')
    await OrderFSM.conformation.set()
    if delivery_type.pk != 1:
        if standard:
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
                             f"📅 <b>Дата доставки:</b> {delivery_date.strftime('%d.%m.%Y')}\n\n"
                             f"🕒 <b>Время доставки:</b> {delivery_start_time} - {delivery_end_time}\n\n"
                             f"🏠 <b>Адрес доставки:</b> {delivery_address}\n\n"
                             f"💬 <b>Комментарий для курьера:</b> {delivery_comment}\n\n"
                             f"📞 <b>Номер телефона:</b> {phone_number}\n\n"
                             f"👤 <b>Имя контактного лица:</b> {contact_name}\n\n"
                             f"💰 <b>Итоговая стоимость торта c доставкой:</b> {total_cake_price + delivery_price}\n\n",
                             reply_markup=await get_conformation_keyboard(),
                             parse_mode='HTML',
                             )
        else:
            await message.answer("📝 Пожалуйста, проверьте правильность введенных данных:\n\n"
                                 f"🎂 <b>Торт:</b> {cake.name}\n\n"
                                 f"📝 <b>Описание:</b> уровней - {level}, форма - {form}, топпинг - {topping}, "
                                 f"ягода - {berry}, декор - {decoration}\n\n"
                                 f"📝 <b>Надпись:</b> {cake_text}\n\n"
                                 f"💬 <b>Комментарий к торту:</b> {cake_comment}\n\n"
                                 f"🚚 <b>Способ доставки:</b> {delivery_type}\n\n"
                                 f"📅 <b>Дата доставки:</b> {delivery_date.strftime('%d.%m.%Y')}\n\n"
                                 f"🕒 <b>Время доставки:</b> {delivery_start_time} - {delivery_end_time}\n\n"
                                 f"🏠 <b>Адрес доставки:</b> {delivery_address}\n\n"
                                 f"💬 <b>Комментарий для курьера:</b> {delivery_comment}\n\n"
                                 f"📞 <b>Номер телефона:</b> {phone_number}\n\n"
                                 f"👤 <b>Имя контактного лица:</b> {contact_name}\n\n"
                                 f"💰 <b>Итоговая стоимость торта c доставкой:</b> {total_cake_price + delivery_price}\n\n",
                                 reply_markup=await get_conformation_keyboard(),
                                 parse_mode='HTML',
                                 )
    else:
        if standard:
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
                             f"📅 <b>Дата доставки:</b> {delivery_date.strftime('%d.%m.%Y')}\n\n"
                             f"📞 <b>Номер телефона:</b> {phone_number}\n\n"
                             f"👤 <b>Имя контактного лица:</b> {contact_name}\n\n"
                             f"💰 <b>Итоговая стоимость торта c доставкой:</b> {total_cake_price + delivery_price}\n\n",
                             reply_markup=await get_conformation_keyboard(),
                             parse_mode='HTML',
                             )
        else:
            await message.answer("📝 Пожалуйста, проверьте правильность введенных данных:\n\n"
                                 f"🎂 <b>Торт:</b> {cake.name}\n\n"
                                 f"📝 <b>Описание:</b> уровней - {level}, форма - {form}, топпинг - {topping}, "
                                 f"ягода - {berry}, декор - {decoration}\n\n"
                                 f"📝 <b>Надпись:</b> {cake_text}\n\n"
                                 f"💬 <b>Комментарий к торту:</b> {cake_comment}\n\n"
                                 f"🚚 <b>Способ доставки:</b> {delivery_type}\n\n"
                                 f"📅 <b>Дата доставки:</b> {delivery_date.strftime('%d.%m.%Y')}\n\n"
                                 f"📞 <b>Номер телефона:</b> {phone_number}\n\n"
                                 f"👤 <b>Имя контактного лица:</b> {contact_name}\n\n"
                                 f"💰 <b>Итоговая стоимость торта c доставкой:</b> {total_cake_price + delivery_price}\n\n",
                                 reply_markup=await get_conformation_keyboard(),
                                 parse_mode='HTML',
                                 )


async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    logger.info('Try to create order')
    status = await sync_to_async(OrderStatus.objects.get)(pk=1)
    try:
        async with state.proxy() as data:
            try:
                client, _ = await sync_to_async(Client.objects.get_or_create)(
                    chat_id=callback.from_user.id,
                    defaults={
                        'personal_data_consent': True,
                        'first_name': data['contact_name'],
                    }
                )
                logger.info(f'{client}')
            except:
                logger.error('Не получилось добавить клиента в базу', exc_info=True)
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
            logger.info(f'Order number: {order.pk}')
            if data['delivery_type'].pk == 1:
                delivery_time = await sync_to_async(DeliveryTime.objects.create)(
                    order=order,
                    delivery_date=data['delivery_date'],
                    delivery_status='initial',
                )
            else:
                delivery_time = await sync_to_async(DeliveryTime.objects.create)(
                    order=order,
                    delivery_date=data['delivery_date'],
                    delivery_time=data['delivery_time'],
                    delivery_status='initial',
                )
            logger.info(f'Delivery: {delivery_time.delivery_date} {delivery_time.delivery_time}')
            if not order.cake.standard:
                logger.info(f'Cake is not standard')
                await sync_to_async(order.ingredients.add)(data['topping'])
                await sync_to_async(order.save)()
                get_first_topping = await sync_to_async(order.ingredients.first)()
                logger.info(f'Ingredients: {get_first_topping.name}')
                if data['berry']:
                    await sync_to_async(order.ingredients.add)(data['berry'])
                    await sync_to_async(order.save)()
                if data['decoration']:
                    await sync_to_async(order.ingredients.add)(data['decoration'])
                    await sync_to_async(order.save)()
    except:
        logger.error(f'Ошибка записи в базу данных, data: {data}', exc_info=True)
        await callback.message.answer(
            "К сожалению, не получилось оформить Ваш заказ!\n\n"
            "Пожалуйста, свяжитесь с нами по телефону: +7 (495) 456-56-56.",
            reply_markup=await get_just_main_menu_keyboard(),
            parse_mode='HTML',
        )
    else:
        await callback.message.answer(
            f"Ваш заказ <b>№{ order.pk }</b> успешно создан!",
            reply_markup=await get_just_main_menu_keyboard(),
            parse_mode='HTML',
        )
    finally:
        await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    await bot.send_message(message.from_user.id,
                           text='Выполнена отмена, все промежуточные данные очищены',
                           reply_markup=ReplyKeyboardRemove())
    await bot.send_message(message.from_user.id,
                           '🤖 ГЛАВНОЕ МЕНЮ:',
                           parse_mode='HTML',
                           reply_markup=await get_main_menu_keyboard(),
                           )


async def get_my_orders_handler(callback: types.callback_query) -> None:
    logger.info('Try to get my orders')
    order_exist = False
    try:
        client = await sync_to_async(Client.objects.get)(chat_id=callback.from_user.id)
        logger.info(f'Client: {client}')
        order_exist = await sync_to_async(Order.objects.filter(client=client).exists)()
        logger.info(f'Order exist: {order_exist}')
    except:
        logger.error('Клиента нет в базе', exc_info=True)
    if order_exist:
        await callback.message.edit_text('Выберите заказ, чтобы посмотреть подробности:',
                                     reply_markup=await get_my_orders_keyboard(client),
                                     parse_mode='HTML',
                                     )
    else:
        await callback.message.edit_text('У Вас пока нет заказов',
                                         reply_markup=await get_just_main_menu_keyboard(),
                                         parse_mode='HTML',
                                         )


async def get_order_details_handler(callback: types.callback_query) -> None:
    logger.info('Try to get order details')
    client = await sync_to_async(Client.objects.get)(chat_id=callback.from_user.id)
    logger.info(f'Client: {client}')
    order_id = int(callback.data.split('_')[-1])
    logger.info(f'Order id: {order_id}')
    order = await sync_to_async(Order.objects.filter(pk=order_id)
                                .select_related('cake')
                                .select_related('delivery_type')
                                .select_related('status')
                                .prefetch_related('ingredients')
                                .prefetch_related('delivery_time')
                                .first)()
    date = ''
    time = ''
    ingredients = []
    async for delivery_time in order.delivery_time.all():
        logger.info(f'Delivery time: {delivery_time.delivery_date} {delivery_time.delivery_time}')
        date = delivery_time.delivery_date
        time = delivery_time.delivery_time
    logger.info(f'Order: {order.cake.name} {order.delivery_type.name} {date} {order.cake_comment}')
    async for ingredient in order.ingredients.all():
        ingredients.append(ingredient.name)
    ingredients_str = ', '.join(ingredients)
    logger.info(f'Ingredients: {ingredients_str}')
    if order.delivery_type.pk != 1:
        if order.cake.standard:
            await callback.message.edit_text("📝 Данные Вашего заказа:\n\n"
                                     f"🎂 <b>Торт:</b> {order.cake.name}\n\n"
                                     f"📝 <b>Надпись:</b> {order.text}\n\n"
                                     f"💬 <b>Комментарий к торту:</b> {order.cake_comment}\n\n"
                                     f"🚚 <b>Способ доставки:</b> {order.delivery_type.name}\n\n"
                                             f"📅 <b>Дата доставки:</b> {date.strftime('%d.%m.%Y')}\n\n"
                                             f"🕒 <b>Время доставки:</b> в течение 2-х часов с {time}\n\n"
                                     f"🏠 <b>Адрес доставки:</b> {order.delivery_address}\n\n"
                                     f"💬 <b>Комментарий для курьера:</b> {order.delivery_comment}\n\n"
                                     f"📞 <b>Номер телефона:</b> {order.contact_phone}\n\n"
                                     f"👤 <b>Имя контактного лица:</b> {order.contact_name}\n\n"
                                            f"👤 <b>Статус заказа:</b> {order.status.name}\n\n"
                                     f"💰 <b>Итоговая стоимость торта c доставкой:</b> {order.total_cake_price + order.total_delivery_price}\n\n",
                                     reply_markup=await get_just_main_menu_keyboard(),
                                     parse_mode='HTML',
                                     )
        else:
            await callback.message.edit_text("📝 Данные Вашего заказа:\n\n"
                                     f"🎂 <b>Торт:</b> {order.cake.name}\n\n"
                                             f"📝 <b>Ингредиенты:</b> {ingredients_str}\n\n"
                                     f"📝 <b>Надпись:</b> {order.text}\n\n"
                                     f"💬 <b>Комментарий к торту:</b> {order.cake_comment}\n\n"
                                     f"🚚 <b>Способ доставки:</b> {order.delivery_type.name}\n\n"
                                             f"📅 <b>Дата доставки:</b> {date.strftime('%d.%m.%Y')}\n\n"
                                             f"🕒 <b>Время доставки:</b> в течение 2-х часов с {time}\n\n"
                                     f"🏠 <b>Адрес доставки:</b> {order.delivery_address}\n\n"
                                     f"💬 <b>Комментарий для курьера:</b> {order.delivery_comment}\n\n"
                                     f"📞 <b>Номер телефона:</b> {order.contact_phone}\n\n"
                                     f"👤 <b>Имя контактного лица:</b> {order.contact_name}\n\n"
                                            f"👤 <b>Статус заказа:</b> {order.status.name}\n\n"
                                     f"💰 <b>Итоговая стоимость торта c доставкой:</b> {order.total_cake_price + order.total_delivery_price}\n\n",
                                     reply_markup=await get_just_main_menu_keyboard(),
                                     parse_mode='HTML',
                                     )
    else:
        if order.cake.standard:
            await callback.message.edit_text("📝 Данные Вашего заказа:\n\n"
                                             f"🎂 <b>Торт:</b> {order.cake.name}\n\n"
                                             f"📝 <b>Надпись:</b> {order.text}\n\n"
                                             f"💬 <b>Комментарий к торту:</b> {order.cake_comment}\n\n"
                                             f"🚚 <b>Способ доставки:</b> {order.delivery_type.name}\n\n"
                                             f"📅 <b>Дата самовывоза:</b> {date.strftime('%d.%m.%Y')}\n\n"
                                             f"📞 <b>Номер телефона:</b> {order.contact_phone}\n\n"
                                             f"👤 <b>Имя контактного лица:</b> {order.contact_name}\n\n"
                                             f"👤 <b>Статус заказа:</b> {order.status.name}\n\n"
                                             f"💰 <b>Итоговая стоимость торта c доставкой:</b> {order.total_cake_price + order.total_delivery_price}\n\n",
                                             reply_markup=await get_just_main_menu_keyboard(),
                                             parse_mode='HTML',
                                             )
        else:
            await callback.message.edit_text("📝 Данные Вашего заказа:\n\n"
                                             f"🎂 <b>Торт:</b> {order.cake.name}\n\n"
                                             f"📝 <b>Ингредиенты:</b> {ingredients_str}\n\n"
                                             f"📝 <b>Надпись:</b> {order.text}\n\n"
                                             f"💬 <b>Комментарий к торту:</b> {order.cake_comment}\n\n"
                                             f"🚚 <b>Способ доставки:</b> {order.delivery_type.name}\n\n"
                                             f"📅 <b>Дата самовывоза:</b> {date.strftime('%d.%m.%Y')}\n\n"
                                             f"📞 <b>Номер телефона:</b> {order.contact_phone}\n\n"
                                             f"👤 <b>Имя контактного лица:</b> {order.contact_name}\n\n"
                                             f"👤 <b>Статус заказа:</b> {order.status.name}\n\n"
                                             f"💰 <b>Итоговая стоимость торта c доставкой:</b> {order.total_cake_price + order.total_delivery_price}\n\n",
                                             reply_markup=await get_just_main_menu_keyboard(),
                                             parse_mode='HTML',
                                             )


def register_user_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров для пользователей."""

    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')
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
    dp.register_callback_query_handler(start_create_cake_handler,
                                lambda callback_query: callback_query.data == 'start_creating_cake',
                                state='*',
                                )
    dp.register_callback_query_handler(start_choose_cake_handler,
                                       lambda callback_query: callback_query.data == 'choose_cake',
                                       state='*',
                                       )
    dp.register_message_handler(no_berries_handler, state=CreateCakeFSM.add_berries)
    dp.register_message_handler(no_decoration_handler, state=CreateCakeFSM.add_decor)
    dp.register_callback_query_handler(choose_level_handler,
                                       lambda callback_query: callback_query.data.startswith('level_'),
                                       state=CreateCakeFSM.choose_level,
                                       )
    dp.register_callback_query_handler(choose_form_handler,
                                       lambda callback_query: callback_query.data.startswith('form_'),
                                       state=CreateCakeFSM.choose_form,
                                       )
    dp.register_callback_query_handler(start_order_handler,
                                       lambda callback_query: callback_query.data == 'start_order',
                                       )
    dp.register_callback_query_handler(FAQ_handler,
                                       lambda callback_query: callback_query.data == 'FAQ',
                                       )
    dp.register_callback_query_handler(get_main_menu_handler,
                                       lambda callback_query: callback_query.data == 'main_menu',
                                       state='*',
                                       )
    dp.register_callback_query_handler(get_my_orders_handler,
                                        lambda callback_query: callback_query.data == 'my_orders',
                                        state='*',
                                       )
    dp.register_callback_query_handler(get_order_details_handler,
                                        lambda callback_query: callback_query.data.startswith('order_'),
                                        state='*',
                                       )


if __name__ == "__main__":
    print(datetime.date(2023, 7, 31))
