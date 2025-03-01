"""
Middleware for request rate limiting
"""
import time
from typing import Dict, Any, Callable, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.dispatcher.flags import get_flag


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for limiting the frequency of user requests
    """
    
    def __init__(self, default_rate: float = 0.5):
        """
        Initialize middleware
        
        Args:
            default_rate: Minimum interval between requests in seconds
        """
        self.default_rate = default_rate
        self.user_last_request: Dict[int, float] = {}
    
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
        # Get user from event
        user = self._get_user(event)
        
        if user:
            # Get throttling_rate flag from handler or use default value
            # Modified for compatibility with aiogram 3.15.0
            throttling_rate = get_flag(data, "throttling_rate") or self.default_rate
            
            # If flag is 0, disable rate limiting for this handler
            if throttling_rate <= 0:
                return await handler(event, data)
            
            # Get time of last request from user
            user_id = user.id
            last_request_time = self.user_last_request.get(user_id, 0)
            current_time = time.time()
            
            # Check if enough time has passed since the last request
            if current_time - last_request_time < throttling_rate:
                # If not enough time has passed, ignore the request
                return None
            
            # Update last request time
            self.user_last_request[user_id] = current_time
        
        # Call event handler
        return await handler(event, data)
    
    def _get_user(self, event: TelegramObject) -> Optional[Any]:
        """
        Get user from event
        
        Args:
            event: Event
            
        Returns:
            Optional[Any]: User or None if user not found
        """
        if isinstance(event, Message):
            return event.from_user
        elif isinstance(event, CallbackQuery):
            return event.from_user
        return None 