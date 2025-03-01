"""
Localization module for the bot
"""
from typing import Dict, Any

from bot.locales import ru, en


class Localization:
    """Class for working with localizations"""
    
    def __init__(self, default_language: str = "en"):
        """
        Initialize localization
        
        Args:
            default_language: Default language
        """
        self.languages = {
            "ru": ru,
            "en": en
        }
        self.default_language = default_language
    
    def get_message(self, key: str, language: str, **kwargs) -> str:
        """
        Get message by key and language
        
        Args:
            key: Message key
            language: Language code
            **kwargs: Formatting parameters
            
        Returns:
            str: Formatted message
        """
        if language not in self.languages:
            language = self.default_language
            
        messages = self.languages[language].MESSAGES
        
        if key not in messages:
            # If key not found in selected language, try to find in default language
            messages = self.languages[self.default_language].MESSAGES
            if key not in messages:
                return f"Message key '{key}' not found"
        
        message = messages[key]
        
        # Format message if parameters are provided
        if kwargs:
            try:
                return message.format(**kwargs)
            except KeyError:
                return message
        
        return message
    
    def get_button(self, key: str, language: str) -> str:
        """
        Get button text by key and language
        
        Args:
            key: Button key
            language: Language code
            
        Returns:
            str: Button text
        """
        if language not in self.languages:
            language = self.default_language
            
        buttons = self.languages[language].BUTTONS
        
        if key not in buttons:
            # If key not found in selected language, try to find in default language
            buttons = self.languages[self.default_language].BUTTONS
            if key not in buttons:
                return f"Button key '{key}' not found"
        
        return buttons[key]
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Get list of available languages
        
        Returns:
            Dict[str, str]: Dictionary with language codes and their names
        """
        return {
            lang: self.get_button(lang, lang)
            for lang in self.languages.keys()
        }


# Create localization instance for use in other modules
localization = Localization() 