import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import FSInputFile

from config import BOT_TOKEN
from lexicon import LEXICON, LEXICON_RU, LEXICON_EN

logging.basicConfig(level=logging.INFO)

user_lang = {}

def get_lang(user_id: int) -> str:
    return user_lang.get(user_id, 'ru')

# --- Клавиатуры ---

def get_main_kb(lang: str):
    lex = LEXICON[lang]
    builder = ReplyKeyboardBuilder()
    builder.button(text=lex['btn_experience'])
    builder.button(text=lex['btn_gallery'])
    builder.button(text=lex['btn_about'])
    builder.button(text=lex['btn_contacts'])
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

def get_welcome_inline_kb(lang: str):
    lex = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=lex['lang_btn'], callback_data="toggle_lang")
    return builder.as_markup()

def get_experience_inline_kb(lang: str):
    lex = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=lex['btn_e_milestone1'], callback_data="exp_milestone1")
    builder.button(text=lex['btn_e_milestone2'], callback_data="exp_milestone2")
    builder.button(text=lex['btn_e_milestone3'], callback_data="exp_milestone3")
    builder.adjust(1)
    return builder.as_markup()

def get_about_inline_kb(lang: str):
    lex = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=lex['btn_a_history'], callback_data="about_history")
    builder.button(text=lex['btn_a_lifestyle'], callback_data="about_lifestyle")
    builder.button(text=lex['btn_a_tech'], callback_data="about_tech")
    builder.adjust(1)
    return builder.as_markup()

def get_gallery_inline_kb(lang: str):
    lex = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=lex['btn_g_archive'], callback_data="g_archive")
    builder.button(text=lex['btn_g_cases'], callback_data="g_cases")
    builder.button(text=lex['btn_g_video'], callback_data="g_video")
    builder.adjust(1)
    return builder.as_markup()

# --- Хэндлеры ---

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    lang = get_lang(message.from_user.id)
    lex = LEXICON[lang]
    
    try:
        photo = FSInputFile("images/start1.jpg")
        await message.answer_photo(
            photo=photo,
            caption=lex['welcome'],
            reply_markup=get_welcome_inline_kb(lang),
            parse_mode=ParseMode.HTML
        )
    except Exception:
        await message.answer(
            lex['welcome'],
            reply_markup=get_welcome_inline_kb(lang),
            parse_mode=ParseMode.HTML
        )
        
    await message.answer(
        "👇",
        reply_markup=get_main_kb(lang),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data == "toggle_lang")
async def toggle_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_lang = get_lang(user_id)
    new_lang = 'en' if current_lang == 'ru' else 'ru'
    user_lang[user_id] = new_lang
    lex = LEXICON[new_lang]

    # Безопасное обновление текста карточки/приветствия
    try:
        await callback.message.edit_caption(
            caption=lex['welcome'],
            reply_markup=get_welcome_inline_kb(new_lang),
            parse_mode=ParseMode.HTML
        )
    except Exception:
        await callback.message.edit_text(
            text=lex['welcome'],
            reply_markup=get_welcome_inline_kb(new_lang),
            parse_mode=ParseMode.HTML
        )

    await callback.message.answer(
        lex['lang_switched'],
        reply_markup=get_main_kb(new_lang),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@dp.message(F.text.in_({LEXICON_RU['btn_experience'], LEXICON_EN['btn_experience']}))
async def show_experience(message: types.Message):
    lang = get_lang(message.from_user.id)
    lex = LEXICON[lang]
    await message.answer(lex['exp_text'], reply_markup=get_experience_inline_kb(lang), parse_mode=ParseMode.HTML)

@dp.message(F.text.in_({LEXICON_RU['btn_gallery'], LEXICON_EN['btn_gallery']}))
async def show_gallery(message: types.Message):
    lang = get_lang(message.from_user.id)
    lex = LEXICON[lang]
    await message.answer(lex['gallery_text'], reply_markup=get_gallery_inline_kb(lang), parse_mode=ParseMode.HTML)

@dp.message(F.text.in_({LEXICON_RU['btn_about'], LEXICON_EN['btn_about']}))
async def show_about(message: types.Message):
    lang = get_lang(message.from_user.id)
    lex = LEXICON[lang]
    await message.answer(lex['about_text'], reply_markup=get_about_inline_kb(lang), parse_mode=ParseMode.HTML)

@dp.message(F.text.in_({LEXICON_RU['btn_contacts'], LEXICON_EN['btn_contacts']}))
async def show_contacts(message: types.Message):
    lang = get_lang(message.from_user.id)
    lex = LEXICON[lang]
    
    try:
        photo = FSInputFile("images/con1.jpg")
        await message.answer_photo(
            photo=photo,
            caption=lex['contacts_text'],
            parse_mode=ParseMode.HTML
        )
    except Exception:
        await message.answer(lex['contacts_text'], parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# Callback-обработчики контентных подразделов
@dp.callback_query(F.data.startswith(("exp_", "about_", "g_")))
async def process_content_callbacks(callback: types.CallbackQuery):
    lang = get_lang(callback.from_user.id)
    key = callback.data
    lex = LEXICON[lang]
    text = lex.get(key, "Information loading...")

    photo_map = {
        "exp_milestone1": "images/ex1.jpg",
        "exp_milestone2": "images/ex2.jpg",
        "exp_milestone3": "images/ex3.jpg",
        "about_history": "images/me1.jpg",
    }

    image_path = photo_map.get(key)

    if image_path:
        try:
            photo = FSInputFile(image_path)
            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                parse_mode=ParseMode.HTML
            )
        except Exception:
            await callback.message.answer(text, parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer(text, parse_mode=ParseMode.HTML)

    await callback.answer()

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())