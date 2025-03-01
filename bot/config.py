"""
Bot configuration
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Bot configuration"""
    
    # Telegram bot token
    bot_token: str = Field(
        default=os.getenv("BOT_TOKEN", ""),
        description="Telegram bot token"
    )
    
    # URL of local Telegram API server
    local_api_url: Optional[str] = Field(
        default=os.getenv("LOCAL_API_URL", None),
        description="URL of local Telegram API server"
    )
    
    # Directory for downloaded files
    download_dir: str = Field(
        default=os.getenv("DOWNLOAD_DIR", "downloads"),
        description="Directory for downloaded files"
    )
    
    # Timeout for download operations (in seconds)
    timeout: int = Field(
        default=int(os.getenv("TIMEOUT", "60")),
        description="Timeout for download operations (in seconds)"
    )
    
    # Debug mode
    debug: bool = Field(
        default=os.getenv("DEBUG", "False").lower() in ("true", "1", "t"),
        description="Debug mode"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Create download directory if it doesn't exist
        download_path = Path(self.download_dir)
        if not download_path.exists():
            download_path.mkdir(parents=True, exist_ok=True)


# Create configuration instance for use in other modules
config = Config() 