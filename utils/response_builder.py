"""Response builder for consistent message formatting"""
from typing import Optional, Dict, Any
from telegram import InlineKeyboardMarkup
from constants.response_fields import ResponseFields

class ResponseBuilder:
    """Builder for creating consistent bot responses"""
    
    @staticmethod
    def success(message: str, keyboard: Optional[InlineKeyboardMarkup] = None) -> Dict[str, Any]:
        """Create a success response
        
        Args:
            message: The success message
            keyboard: Optional inline keyboard
            
        Returns:
            Response dictionary
        """
        return {
            ResponseFields.TEXT: f"✅ {message}",
            ResponseFields.KEYBOARD: keyboard,
            ResponseFields.PARSE_MODE: None
        }
    
    @staticmethod
    def error(message: str, keyboard: Optional[InlineKeyboardMarkup] = None) -> Dict[str, Any]:
        """Create an error response
        
        Args:
            message: The error message
            keyboard: Optional inline keyboard
            
        Returns:
            Response dictionary
        """
        return {
            ResponseFields.TEXT: f"❌ {message}",
            ResponseFields.KEYBOARD: keyboard,
            ResponseFields.PARSE_MODE: None
        }
    
    @staticmethod
    def info(message: str, keyboard: Optional[InlineKeyboardMarkup] = None) -> Dict[str, Any]:
        """Create an info response
        
        Args:
            message: The info message
            keyboard: Optional inline keyboard
            
        Returns:
            Response dictionary
        """
        return {
            ResponseFields.TEXT: f"ℹ️ {message}",
            ResponseFields.KEYBOARD: keyboard,
            ResponseFields.PARSE_MODE: None
        }
    
    @staticmethod
    def warning(message: str, keyboard: Optional[InlineKeyboardMarkup] = None) -> Dict[str, Any]:
        """Create a warning response
        
        Args:
            message: The warning message
            keyboard: Optional inline keyboard
            
        Returns:
            Response dictionary
        """
        return {
            ResponseFields.TEXT: f"⚠️ {message}",
            ResponseFields.KEYBOARD: keyboard,
            ResponseFields.PARSE_MODE: None
        }
    
    @staticmethod
    def custom(
        message: str,
        emoji: str = "",
        keyboard: Optional[InlineKeyboardMarkup] = None,
        parse_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a custom response
        
        Args:
            message: The message text
            emoji: Optional emoji prefix
            keyboard: Optional inline keyboard
            parse_mode: Optional parse mode (HTML, Markdown, etc.)
            
        Returns:
            Response dictionary
        """
        text = f"{emoji} {message}" if emoji else message
        return {
            ResponseFields.TEXT: text,
            ResponseFields.KEYBOARD: keyboard,
            ResponseFields.PARSE_MODE: parse_mode
        }
    
    @staticmethod
    def menu(title: str, keyboard: InlineKeyboardMarkup, parse_mode: Optional[str] = None) -> Dict[str, Any]:
        """Create a menu response
        
        Args:
            title: The menu title
            keyboard: The inline keyboard
            parse_mode: Optional parse mode
            
        Returns:
            Response dictionary
        """
        return {
            ResponseFields.TEXT: title,
            ResponseFields.KEYBOARD: keyboard,
            ResponseFields.PARSE_MODE: parse_mode
        }
