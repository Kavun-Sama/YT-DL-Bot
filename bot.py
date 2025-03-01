"""
YouTube Downloader Telegram Bot

A bot for downloading videos and audio from YouTube with a convenient inline interface.
"""
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.config import config
from bot.handlers import router
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.logging import LoggingMiddleware


# Setup logging
def setup_logging() -> None:
    """Configure logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "bot.log"),
        ]
    )


# Initialize bot and dispatcher
async def main() -> None:
    """Main function to launch the bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create session with local API server if specified
    if config.local_api_url:
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(config.local_api_url)
        )
        logger.info(f"Using local API server: {config.local_api_url}")
    else:
        session = None
    
    # Create bot instance with new method of setting parameters
    bot = Bot(
        token=config.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher
    dp = Dispatcher()
    
    # Register middlewares
    dp.message.middleware(ThrottlingMiddleware(default_rate=0.5))
    dp.callback_query.middleware(ThrottlingMiddleware(default_rate=0.3))
    
    if config.debug:
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
    
    # Register handlers
    dp.include_router(router)
    
    # Start the bot
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 