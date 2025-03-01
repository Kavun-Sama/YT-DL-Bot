"""
Middleware for logging
"""
import logging
from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging events
    """
    
    def __init__(self):
        """
        Initialize middleware
        """
        self.logger = logging.getLogger(__name__)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process event
        
        Args:
            handler: Event handler
            event: Event
            data: Event data
            
        Returns:
            Any: Result of event processing
        """
        # Log incoming event
        self._log_event(event)
        
        # Call event handler
        return await handler(event, data)
    
    def _log_event(self, event: TelegramObject) -> None:
        """
        Log event
        
        Args:
            event: Event
        """
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else "Unknown"
            username = event.from_user.username if event.from_user and event.from_user.username else "Unknown"
            
            if event.text:
                self.logger.info(f"Message from user {user_id} (@{username}): {event.text}")
            elif event.photo:
                self.logger.info(f"Photo from user {user_id} (@{username})")
            elif event.document:
                self.logger.info(f"Document from user {user_id} (@{username}): {event.document.file_name}")
            else:
                self.logger.info(f"Other message type from user {user_id} (@{username})")
        
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else "Unknown"
            username = event.from_user.username if event.from_user and event.from_user.username else "Unknown"
            
            self.logger.info(f"Callback from user {user_id} (@{username}): {event.data}") 