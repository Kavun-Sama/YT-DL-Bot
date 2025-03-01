"""
Inline keyboards for bot
"""
from typing import Dict, List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import localization


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Language selection keyboard
    
    Returns:
        InlineKeyboardMarkup: Keyboard with language selection buttons
    """
    builder = InlineKeyboardBuilder()
    
    # Get available languages
    languages = localization.get_available_languages()
    
    # Add buttons for each language
    for lang_code, lang_name in languages.items():
        builder.add(InlineKeyboardButton(
            text=lang_name,
            callback_data=f"language:{lang_code}"
        ))
    
    # Arrange buttons in one column
    builder.adjust(1)
    
    return builder.as_markup()


def get_format_keyboard(language: str, url: str = None) -> InlineKeyboardMarkup:
    """
    Format selection keyboard (video or audio)
    
    Args:
        language: Language code
        url: Video URL
        
    Returns:
        InlineKeyboardMarkup: Keyboard with format selection buttons
    """
    builder = InlineKeyboardBuilder()
    
    # Add format selection buttons
    builder.add(InlineKeyboardButton(
        text=localization.get_button("video", language),
        callback_data=f"format:video:{url}" if url else "format:video"
    ))
    
    builder.add(InlineKeyboardButton(
        text=localization.get_button("audio", language),
        callback_data=f"format:audio:{url}" if url else "format:audio"
    ))
    
    # Add cancel button
    builder.add(InlineKeyboardButton(
        text=localization.get_button("cancel", language),
        callback_data="cancel"
    ))
    
    # Arrange buttons in one column
    builder.adjust(1)
    
    return builder.as_markup()


def get_video_quality_keyboard(language: str, url: str, available_formats: List[str] = None) -> InlineKeyboardMarkup:
    """
    Video quality selection keyboard
    
    Args:
        language: Language code
        url: Video URL
        available_formats: List of available video formats
        
    Returns:
        InlineKeyboardMarkup: Keyboard with quality selection buttons
    """
    builder = InlineKeyboardBuilder()
    
    # If available formats list is not provided, use standard set
    if not available_formats:
        available_formats = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
    
    # Add quality selection buttons
    for quality in available_formats:
        builder.add(InlineKeyboardButton(
            text=quality,
            callback_data=f"quality:{quality}:{url}"
        ))
    
    # Add navigation buttons
    builder.add(InlineKeyboardButton(
        text=localization.get_button("back", language),
        callback_data=f"back_to_format:{url}"
    ))
    
    builder.add(InlineKeyboardButton(
        text=localization.get_button("cancel", language),
        callback_data="cancel"
    ))
    
    # Determine number of buttons per row depending on the number of formats
    if len(available_formats) <= 4:
        # If there are few formats, place one per row
        builder.adjust(1, 1)
    else:
        # Otherwise place two per row, except navigation buttons
        buttons_per_row = 2
        rows = (len(available_formats) + buttons_per_row - 1) // buttons_per_row
        adjust_values = [buttons_per_row] * rows + [1, 1]  # Last two buttons (back and cancel) in separate rows
        builder.adjust(*adjust_values)
    
    return builder.as_markup() 