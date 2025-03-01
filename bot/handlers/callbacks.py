"""
Callback handlers for inline keyboards
"""
import logging
from typing import Optional
import re

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramAPIError

from bot.locales import localization
from bot.database.models import user_db
from bot.keyboards.inline import get_format_keyboard, get_video_quality_keyboard
from bot.services.youtube import youtube_service

# Create router for callbacks
router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("language:"))
async def callback_language(callback: CallbackQuery) -> None:
    """
    Language selection handler
    
    Args:
        callback: Callback from inline keyboard
    """
    # Get selected language from callback data
    language = callback.data.split(":")[1]
    
    # Save user's selected language
    user_id = callback.from_user.id
    user_db.set_user_language(user_id, language)
    
    # Send language selection message
    await callback.message.edit_text(
        text=localization.get_message("language_selected", language)
    )
    
    # Answer callback
    await callback.answer()


@router.callback_query(F.data.startswith("format:"))
async def callback_format(callback: CallbackQuery) -> None:
    """
    Format selection handler (video or audio)
    
    Args:
        callback: Callback from inline keyboard
    """
    # Get selected format and URL from callback data
    parts = callback.data.split(":")
    format_type = parts[1]
    
    # Get user language
    user_id = callback.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Get video URL from callback data
    url = None
    if len(parts) > 2:
        raw_url = ":".join(parts[2:])  # Join remaining parts, as URL may contain colons
        # Clean URL from extra characters
        url = raw_url.strip()
        url = re.sub(r'^[@\s]+', '', url)
    
    # If URL not found in callback data, try to get it from context
    if not url:
        raw_url = callback.message.reply_to_message.text if callback.message.reply_to_message else None
        if raw_url:
            url = raw_url.strip()
            url = re.sub(r'^[@\s]+', '', url)
    
    if not url or not youtube_service.is_valid_youtube_url(url):
        await callback.message.edit_text(
            text=localization.get_message("invalid_url", language)
        )
        await callback.answer()
        return
    
    if format_type == "video":
        # Show message about getting video information
        await callback.message.edit_text(
            text=localization.get_message("processing", language)
        )
        
        try:
            # Get available video formats
            available_formats = await youtube_service.get_available_formats(url)
            
            # Show video quality selection keyboard with available formats
            await callback.message.edit_text(
                text=localization.get_message("select_quality", language),
                reply_markup=get_video_quality_keyboard(language, url, available_formats)
            )
        except Exception as e:
            logger.error(f"Error getting video formats: {e}")
            # In case of error, show standard keyboard
            await callback.message.edit_text(
                text=localization.get_message("select_quality", language),
                reply_markup=get_video_quality_keyboard(language, url)
            )
    elif format_type == "audio":
        # Start audio download
        await callback.message.edit_text(
            text=localization.get_message("downloading", language)
        )
        
        # Download audio
        file_path, file_name = await youtube_service.download_audio(url)
        
        if file_path and file_name:
            # Send message about file upload
            await callback.message.edit_text(
                text=localization.get_message("uploading", language)
            )
            
            try:
                # Send audio using FSInputFile
                audio_file = FSInputFile(file_path)
                await callback.message.answer_audio(
                    audio=audio_file,
                    title=file_name
                )
                
                # Send download completion message
                await callback.message.edit_text(
                    text=localization.get_message("download_complete", language)
                )
            except TelegramAPIError as e:
                logger.error(f"Error sending audio: {e}")
                await callback.message.edit_text(
                    text=localization.get_message("error", language, error=str(e))
                )
            finally:
                # Delete file after sending
                await youtube_service.cleanup_file(file_path)
        else:
            # Send error message
            await callback.message.edit_text(
                text=localization.get_message("error", language, error="Failed to download audio")
            )
    
    # Answer callback
    await callback.answer()


@router.callback_query(F.data.startswith("quality:"))
async def callback_quality(callback: CallbackQuery) -> None:
    """
    Video quality selection handler
    
    Args:
        callback: Callback from inline keyboard
    """
    # Get selected quality and URL from callback data
    parts = callback.data.split(":")
    quality = parts[1]
    raw_url = ":".join(parts[2:])  # Join remaining parts, as URL may contain colons
    
    # Clean URL from extra characters
    url = raw_url.strip()
    url = re.sub(r'^[@\s]+', '', url)
    
    # Get user language
    user_id = callback.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Start video download
    await callback.message.edit_text(
        text=localization.get_message("downloading", language)
    )
    
    # Check if URL is valid
    if not youtube_service.is_valid_youtube_url(url):
        await callback.message.edit_text(
            text=localization.get_message("invalid_url", language)
        )
        await callback.answer()
        return
    
    # Download video
    try:
        file_path, file_name = await youtube_service.download_video(url, quality)
        
        if file_path and file_name:
            # Send message about file upload
            await callback.message.edit_text(
                text=localization.get_message("uploading", language)
            )
            
            try:
                # Send video using FSInputFile
                video_file = FSInputFile(file_path)
                await callback.message.answer_video(
                    video=video_file,
                    caption=file_name
                )
                
                # Send download completion message
                await callback.message.edit_text(
                    text=localization.get_message("download_complete", language)
                )
            except TelegramAPIError as e:
                logger.error(f"Error sending video: {e}")
                await callback.message.edit_text(
                    text=localization.get_message("error", language, error=str(e))
                )
            finally:
                # Delete file after sending
                await youtube_service.cleanup_file(file_path)
        else:
            # Send error message
            await callback.message.edit_text(
                text=localization.get_message("error", language, error="Failed to download video")
            )
    except Exception as e:
        logger.error(f"Error in video download process: {e}")
        await callback.message.edit_text(
            text=localization.get_message("error", language, error=str(e))
        )
    
    # Answer callback
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_format:"))
async def callback_back_to_format(callback: CallbackQuery) -> None:
    """
    Handler for returning to format selection
    
    Args:
        callback: Callback from inline keyboard
    """
    # Get URL from callback data
    parts = callback.data.split(":")
    raw_url = ":".join(parts[1:])  # Join remaining parts, as URL may contain colons
    
    # Clean URL from extra characters
    url = raw_url.strip()
    url = re.sub(r'^[@\s]+', '', url)
    
    # Get user language
    user_id = callback.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Show format selection keyboard
    await callback.message.edit_text(
        text=localization.get_message("select_format", language),
        reply_markup=get_format_keyboard(language, url)
    )
    
    # Answer callback
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery) -> None:
    """
    Operation cancellation handler
    
    Args:
        callback: Callback from inline keyboard
    """
    # Get user language
    user_id = callback.from_user.id
    language = user_db.get_user_language(user_id)
    
    # Send operation cancellation message
    await callback.message.edit_text(
        text=localization.get_message("operation_cancelled", language)
    )
    
    # Answer callback
    await callback.answer() 