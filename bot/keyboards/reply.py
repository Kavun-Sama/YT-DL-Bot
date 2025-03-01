"""
Обычные клавиатуры для бота
"""
from typing import List, Optional

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.locales import localization


def get_language_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура выбора языка
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками выбора языка
    """
    builder = ReplyKeyboardBuilder()
    
    # Получаем доступные языки
    languages = localization.get_available_languages()
    
    # Добавляем кнопки для каждого языка
    for lang_code, lang_name in languages.items():
        builder.add(KeyboardButton(text=lang_name))
    
    # Размещаем кнопки в одну колонку
    builder.adjust(1)
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_remove_keyboard() -> ReplyKeyboardRemove:
    """
    Удаление клавиатуры
    
    Returns:
        ReplyKeyboardRemove: Объект для удаления клавиатуры
    """
    return ReplyKeyboardRemove() 