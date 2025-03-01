"""
Text message handlers
"""
import re
import logging

from aiogram import Router, F
from aiogram.types import Message

from bot.locales import localization
from bot.database.models import user_db
from bot.keyboards.inline import get_format_keyboard
from bot.services.youtube import youtube_service

# Create router for messages
router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text)
async def handle_text(message: Message) -> None:
    """
    Handler for text messages
    
    Args:
        message: Message from user
    """
    # Get user language
    user_id = message.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Clean message text from extra characters
    text = message.text.strip()
    text = re.sub(r'^[@\s]+', '', text)
    
    logger.info(f"Received message: {text}")
    
    # Check if the message is a YouTube link
    is_youtube = youtube_service.is_valid_youtube_url(text)
    logger.debug(f"YouTube link check result: {is_youtube}")
    
    if is_youtube:
        # Send processing message
        processing_message = await message.answer(
            text=localization.get_message("processing", language)
        )
        
        try:
            # Get video information
            video_info = await youtube_service.get_video_info(text)
            
            # Send message with format selection
            await processing_message.edit_text(
                text=localization.get_message("select_format", language),
                reply_markup=get_format_keyboard(language, text)
            )
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            # Send error message
            await processing_message.edit_text(
                text=localization.get_message("error", language, error=str(e))
            )
    # Check if the message is a language selection
    elif message.text in [localization.get_button("ru", "ru"), localization.get_button("en", "en")]:
        # Determine selected language
        if message.text == localization.get_button("ru", "ru"):
            selected_language = "ru"
        else:
            selected_language = "en"
        
        # Save user language preference
        user_db.set_user_language(user_id, selected_language)
        
        # Send language selection confirmation
        await message.answer(
            text=localization.get_message("language_selected", selected_language)
        ) 