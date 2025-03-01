"""
Handler module for the bot
"""
from aiogram import Router

from bot.handlers import commands, callbacks, messages

# Create the main router
router = Router()

# Include all routers
router.include_router(commands.router)
router.include_router(callbacks.router)
router.include_router(messages.router)

__all__ = ["router"]
