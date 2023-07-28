from aiogram.types import (
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


async def get_just_main_menu_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



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


async def get_order_keyword():
    keyboard=[
        [KeyboardButton(text="🍰 Стандартные торты", web_app=WebAppInfo(url="https://bakecake.6f6e69.xyz/")), ],
        [KeyboardButton(text="🛒 Из моих заказов", web_app=WebAppInfo(url="https://bakecake.6f6e69.xyz/my_cakes/")), ],
        [KeyboardButton(text="🧑‍🍳 Создать свой торт", callback_data="start_create_cake"), ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

