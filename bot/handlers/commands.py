"""
Bot command handlers
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from bot.locales import localization
from bot.database.models import user_db
from bot.keyboards.inline import get_language_keyboard

# Create router for commands
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Handler for /start command
    
    Args:
        message: Message from user
    """
    # Get user language
    user_id = message.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Send welcome message
    await message.answer(
        text=localization.get_message("welcome", language),
        reply_markup=get_language_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Handler for /help command
    
    Args:
        message: Message from user
    """
    # Get user language
    user_id = message.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Send help information
    await message.answer(
        text=localization.get_message("help", language),
        parse_mode="Markdown"
    )


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    """
    Handler for /language command
    
    Args:
        message: Message from user
    """
    # Get user language
    user_id = message.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Send language selection message
    await message.answer(
        text=localization.get_message("select_language", language),
        reply_markup=get_language_keyboard()
    ) 