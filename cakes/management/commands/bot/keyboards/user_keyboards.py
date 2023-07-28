from aiogram.types import (
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

web_app = WebAppInfo(url="https://bakecake.6f6e69.xyz/")

order_keyword = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍰 Стандартные торты", web_app=web_app), ],
        [KeyboardButton(text="🛒 Из моих заказов", web_app=web_app)],
        [KeyboardButton(text="🍯 Создать свой торт", web_app=web_app)],
    ],
    resize_keyboard=True,
)

main_menu_iKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
    ],
]
)
