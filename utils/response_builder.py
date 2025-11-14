"""Response builder for consistent message formatting"""
from typing import Optional, Dict, Any
from telegram import InlineKeyboardMarkup


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
            'text': f"✅ {message}",
            'keyboard': keyboard,
            'parse_mode': None
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
            'text': f"❌ {message}",
            'keyboard': keyboard,
            'parse_mode': None
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
            'text': f"ℹ️ {message}",
            'keyboard': keyboard,
            'parse_mode': None
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
            'text': f"⚠️ {message}",
            'keyboard': keyboard,
            'parse_mode': None
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
            'text': text,
            'keyboard': keyboard,
            'parse_mode': parse_mode
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
            'text': title,
            'keyboard': keyboard,
            'parse_mode': parse_mode
        }
