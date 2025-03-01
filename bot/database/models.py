"""
Data models for working with users and their settings
"""
from typing import Dict, Any, Optional
import json
from pathlib import Path


class UserSettings:
    """Class for storing user settings"""
    
    def __init__(self, user_id: int, language: str = "en"):
        """
        Initialize user settings
        
        Args:
            user_id: User ID
            language: User language
        """
        self.user_id = user_id
        self.language = language
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary
        
        Returns:
            Dict[str, Any]: Dictionary with settings
        """
        return {
            "user_id": self.user_id,
            "language": self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """
        Create settings object from dictionary
        
        Args:
            data: Dictionary with settings
            
        Returns:
            UserSettings: Settings object
        """
        return cls(
            user_id=data.get("user_id"),
            language=data.get("language", "en")
        )


class UserDatabase:
    """Simple database for storing user settings in a JSON file"""
    
    def __init__(self, db_path: str = "bot/database/users.json"):
        """
        Initialize database
        
        Args:
            db_path: Path to database file
        """
        self.db_path = Path(db_path)
        self._ensure_db_exists()
        self._users: Dict[int, UserSettings] = self._load_users()
    
    def _ensure_db_exists(self) -> None:
        """Ensure that the database file exists"""
        if not self.db_path.exists():
            # Create directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            # Create empty file with empty dictionary
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict[int, UserSettings]:
        """
        Load users from file
        
        Returns:
            Dict[int, UserSettings]: Dictionary with users
        """
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    int(user_id): UserSettings.from_dict({**user_data, "user_id": int(user_id)})
                    for user_id, user_data in data.items()
                }
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self) -> None:
        """Save users to file"""
        data = {
            str(user_id): user.to_dict()
            for user_id, user in self._users.items()
        }
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_user(self, user_id: int) -> Optional[UserSettings]:
        """
        Get user settings
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[UserSettings]: User settings or None if user not found
        """
        return self._users.get(user_id)
    
    def add_or_update_user(self, user: UserSettings) -> None:
        """
        Add or update user
        
        Args:
            user: User settings
        """
        self._users[user.user_id] = user
        self._save_users()
    
    def set_user_language(self, user_id: int, language: str) -> None:
        """
        Set user language
        
        Args:
            user_id: User ID
            language: Language code
        """
        user = self.get_user(user_id)
        if user:
            user.language = language
        else:
            user = UserSettings(user_id=user_id, language=language)
        
        self.add_or_update_user(user)
    
    def get_user_language(self, user_id: int, default: str = "en") -> str:
        """
        Get user language
        
        Args:
            user_id: User ID
            default: Default language
            
        Returns:
            str: Language code
        """
        user = self.get_user(user_id)
        return user.language if user else default


# Create database instance for use in other modules
user_db = UserDatabase() 