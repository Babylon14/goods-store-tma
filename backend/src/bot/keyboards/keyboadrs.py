from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


def get_main_menu(webapp_url: str):
    """Главное меню с кнопкой открытия Mini App"""
    
    keyboard = ReplyKeyboardMarkup(keyboard=[
        # Эта кнопка откроет React-фронтенд внутри Telegram
        [KeyboardButton(text="Открыть магазин 🛍️", web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text="О нас"), KeyboardButton(text="Помощь")]
    ], resize_keyboard=True
    )
    return keyboard


