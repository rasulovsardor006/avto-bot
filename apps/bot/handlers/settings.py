from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.cache import cache
from apps.bot.models import User
from apps.bot.keyboards.inline import inline_languages, inline_main_menu
from apps.bot.utils.callback_data import (
    MainMenuCallbackData, MainMenuAction,
 BackToMainMenuAction, cb_back_to_main_menu_callback_data,
)

router = Router()


#
@router.callback_query(MainMenuCallbackData.filter(F.action == MainMenuAction.SETTINGS))
async def settings(callback_query: CallbackQuery):
    user = callback_query.from_user
    user_data = await User.objects.filter(telegram_id=user.id).afirst()

    if not user_data:
        await callback_query.message.edit_text(
            "Iltimos avval ro'yxatdan o'ting \nTilni tanlang:",
            reply_markup=inline_languages()
        )
        return

    lang = user_data.language
    language = "O'zbek" if lang == "uz" else "Русский" if lang == "ru" else "English"

    await callback_query.message.edit_text(
        f"<b>Muloqot tili: </b>{language}\n",
        parse_mode="HTML",
        reply_markup=inline_settings()
    )

def inline_settings():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🌐 Muloqot tili", callback_data="change_language")
    keyboard.button(
        text="🏠 Asosiy menyu",
        callback_data=cb_back_to_main_menu_callback_data(action=BackToMainMenuAction.BACK)
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def inline_languages():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🇺🇿 O'zbek", callback_data="set_language:uz")
    keyboard.button(text="🇷🇺 Русский", callback_data="set_language:ru")
    keyboard.button(text="🇬🇧 English", callback_data="set_language:en")
    keyboard.adjust(1)
    return keyboard.as_markup()


@router.callback_query(F.data == "change_language")
async def change_language(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "🌐 Tilni tanlang:",
        reply_markup=inline_languages()
    )


@router.callback_query(lambda c: c.data.startswith("set_language"))
async def set_language(callback: CallbackQuery):
    language_code = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user = await User.objects.filter(telegram_id=user_id).afirst()

    if not user:
        await callback.message.edit_text(
            "Iltimos avval ro'yxatdan o'ting",
            reply_markup=inline_main_menu()
        )
        return

    user.language = language_code
    await user.asave()

    cache_key = f"user_language_{user_id}"
    cache.set(cache_key, language_code, timeout=3600)

    text = "✅ Til muvaffaqiyatli O'zbek tiliga o'zgartirildi." if language_code == "uz" else \
        "✅ Язык успешно изменён на Русский." if language_code == "ru" else \
            "✅ Language successfully changed to English."

    if callback.message.text != text:
        await callback.message.edit_text(text=text,
                                         reply_markup=inline_settings())
