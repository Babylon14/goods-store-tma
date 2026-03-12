from aiogram import Router, F
from aiogram.types import Message

from src.bot.utils.texts import ABOUT_US, HELP_TEXT


router = Router()

@router.message(F.text == "🚀 О нас")
async def about_us_handler(message: Message):
    await message.answer(ABOUT_US, parse_mode="HTML")


@router.message(F.text == "❓ Помощь")
async def help_handler(message: Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")



