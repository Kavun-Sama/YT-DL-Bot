"""
Модуль промежуточного ПО для бота
"""
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.logging import LoggingMiddleware

__all__ = ["ThrottlingMiddleware", "LoggingMiddleware"]
