from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu(webapp_url: str):
    """Главное меню с кнопкой открытия Mini App"""

    builder = ReplyKeyboardBuilder()
    builder.button(text="Открыть магазин 🛍️", web_app=WebAppInfo(url=webapp_url))
    builder.button(text="📦 Мои заказы")
    builder.button(text="🚀 О нас")
    builder.button(text="❓ Помощь")
    builder.adjust(1, 1, 2)
    return builder.as_markup(resize_keyboard=True)



