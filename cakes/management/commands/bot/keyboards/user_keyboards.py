from datetime import datetime
import calendar
import logging.config

from aiogram.types import (
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from asgiref.sync import sync_to_async

from cakes.logger_config import logger_config
from cakes.models import DeliveryType, Level, Form, Order, DeliveryTime

logger = logging.getLogger("user_keyboards_logger")

logging.config.dictConfig(logger_config)


async def get_just_main_menu_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_main_menu_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Оформить заказ', callback_data='start_order'),
        ],
        [
            InlineKeyboardButton(text='Мои заказы', callback_data='my_orders'),
        ],
        [
            InlineKeyboardButton(text='О нас', callback_data='FAQ'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_my_orders_keyboard(client):
    logger.debug("get_my_orders_keyboard")
    my_orders = await sync_to_async(Order.objects.filter(client=client)
                                .select_related('cake')
                                .select_related('delivery_type')
                                .select_related('status')
                                .prefetch_related('ingredients')
                                .prefetch_related)('delivery_time')

    inline_keyboard = []
    async for order in my_orders:
        async for delivery_time in order.delivery_time.all():
            date = delivery_time.delivery_date
        order_keyboard = [
            [
                InlineKeyboardButton(text=f'Заказ №{order.pk}: {order.cake.name}, {date.strftime("%d.%m")}', callback_data=f"order_{order.pk}"),
            ]
        ]
        inline_keyboard += order_keyboard

    main_menu_keyboard = [
                [
                    InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
                ]
            ]
    inline_keyboard += main_menu_keyboard

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_month_keyboard(month, year):
    logger.info(f"month: {month}, year: {year}")
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    months = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]

    calendar_keyboard = InlineKeyboardMarkup(row_width=7)
    calendar_keyboard.row()
    for day in ["Пн.", "Вт.", "Ср.", "Чт.", "Пт.", "Сб.", "Вс."]:
        calendar_keyboard.insert(InlineKeyboardButton(day, callback_data=' '))

    month_calendar = calendar.monthcalendar(year, int(month))
    filtered_calendar = []

    if month == current_month and year == current_year:
        for week in month_calendar:
            is_empty_week = True
            for day in week:
                if current_day >= day:
                    week[week.index(day)] = 0
                    continue
                else:
                    is_empty_week = False
                    break
            if not is_empty_week:
                filtered_calendar.append(week)
    else:
        logger.debug('Not current month')
        filtered_calendar = month_calendar
    if filtered_calendar == []:
        next_month = (month + 1) % 12
        next_month_year = year + (month + 1) // 12
        return await get_month_keyboard(next_month, next_month_year)
    for week in filtered_calendar:
        calendar_keyboard.row()
        for day in week:
            if (day == 0):
                calendar_keyboard.insert(InlineKeyboardButton(" ", callback_data=' '))
                continue
            calendar_keyboard.insert(InlineKeyboardButton(str(day), callback_data=f'delivery_date_{day}_{month}_{year}'))

    if month == current_month and year == current_year:
        calendar_keyboard.row(
            InlineKeyboardButton(text=" ", callback_data=" "),
            InlineKeyboardButton(text=f"{months[month - 1]}", callback_data=" "),
            InlineKeyboardButton(text="➡️ Вперед", callback_data=f"next_month_{month}_{year}"),
        )
    else:
        calendar_keyboard.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_month_{month}_{year}"),
            InlineKeyboardButton(text=f"{months[month - 1]}", callback_data=" "),
            InlineKeyboardButton(text=" ", callback_data=" "),
        )

    return calendar_keyboard


async def get_delivery_time_keyboard():
    delivery_time_keyboard = InlineKeyboardMarkup(row_width=2)
    delivery_time_keyboard.row()
    for hour in range(10, 21):
        delivery_time_keyboard.insert(InlineKeyboardButton(f"{hour}:00 - {hour + 2}:00", callback_data=f"delivery_time_{hour}"))
    delivery_time_keyboard.row()
    delivery_time_keyboard.insert(InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
    return delivery_time_keyboard


async def get_no_text_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Без надписи', callback_data='no_text'),
        ],
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_no_comment_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Без комментария', callback_data='no_comment'),
        ],
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

async def get_choosing_order_from_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Выбрать торт из каталога', callback_data='choose_cake'),
        ],
        [
            InlineKeyboardButton(text='Создать свой торт', callback_data='start_creating_cake'),
        ],
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_order_keyboard():
    # my_cakes_web_app_url = f"https://bakecake.6f6e69.xyz/my_cakes/{chat_id}"
    keyboard=[
        [KeyboardButton(text="🍰 Стандартные торты", web_app=WebAppInfo(url="https://bit.ly/bakecake_cakes")), ],
        # [KeyboardButton(text="🛒 Из моих заказов", web_app=WebAppInfo(url="https://bakecake.6f6e69.xyz/my_cakes/")), ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_choose_level_keyboard():
    logger.debug("get_choose_level_keyboard")
    levels = await sync_to_async(Level.objects.all)()
    inline_keyboard = []
    async for level in levels:
        delivery_type_keyboard = [
            [
                InlineKeyboardButton(text=f'{level.quantity}', callback_data=f"level_{level.id}"),
                InlineKeyboardButton(text=f'{level.current_price} руб.', callback_data=f"level_{level.id}"),
            ]
        ]
        inline_keyboard += delivery_type_keyboard

    main_menu_keyboard = [
                [
                    InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
                ]
            ]
    inline_keyboard += main_menu_keyboard

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_choose_form_keyboard():
    logger.debug("get_choose_form_keyboard")
    forms = await sync_to_async(Form.objects.all)()
    inline_keyboard = []
    async for form in forms:
        delivery_type_keyboard = [
            [
                InlineKeyboardButton(text=f'{form.name}', callback_data=f"form_{form.id}"),
                InlineKeyboardButton(text=f'{form.current_price} руб.', callback_data=f"form_{form.id}"),
            ]
        ]
        inline_keyboard += delivery_type_keyboard

    main_menu_keyboard = [
                [
                    InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
                ]
            ]
    inline_keyboard += main_menu_keyboard

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
async def get_choose_topping_keyboard():
    keyboard=[
        [KeyboardButton(text="Выбрать топпинг", web_app=WebAppInfo(url="https://bit.ly/bakecake_toppings")), ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_choose_berry_keyboard():
    keyboard=[
        [KeyboardButton(text="Выбрать ягоды", web_app=WebAppInfo(url="https://bit.ly/bakecake_berries")), ],
        [KeyboardButton(text="Без ягод"), ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_choose_decor_keyboard():
    keyboard=[
        [KeyboardButton(text="Выбрать декор", web_app=WebAppInfo(url="https://bit.ly/bakecake_decoration")), ],
        [KeyboardButton(text="Без декора"), ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_delivery_type_keyboard():
    logger.debug("get_delivery_type_keyboard")
    delivery_types = await sync_to_async(DeliveryType.objects.all)()
    inline_keyboard = []
    async for delivery_type in delivery_types:
        if delivery_type.name == 'Самовывоз':
            delivery_text = 'Самовывоз (м. Пражская, бесплатно)'
        else:
            delivery_text = f'{delivery_type.name} - {int(delivery_type.current_price)} р.'
        delivery_type_keyboard = [
            [
                InlineKeyboardButton(text=delivery_text,
                                     callback_data=f"delivery_type_{delivery_type.id}"),
            ]
        ]
        inline_keyboard += delivery_type_keyboard

    main_menu_keyboard = [
                [
                    InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
                ]
            ]
    inline_keyboard += main_menu_keyboard

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_conformation_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Оформить заказ', callback_data='confirm_order'),
        ],
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
