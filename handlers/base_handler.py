"""Base handler class for all bot handlers"""
from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BaseHandler:
    """Base class for all handlers with common functionality"""
    
    def __init__(self, client):
        """Initialize handler with telegram client
        
        Args:
            client: TelegramClient instance
        """
        self.client = client
        self.logger = logger
    
    def _register_callbacks(self) -> None:
        """Register all decorated callback handlers in app_context"""
        from app_context import app_context
        
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_callback_data'):
                app_context.register_callback(attr._callback_data, attr)
                self.logger.debug(f"Registered callback: {attr._callback_data} -> {attr_name}")
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception) -> None:
        """Handle errors in a consistent way
        
        Args:
            update: The update that caused the error
            context: The context object
            error: The exception that was raised
        """
        self.logger.error(f"Error in handler: {error}", exc_info=True)
        
        if update and update.effective_user:
            from utils.response_builder import ResponseBuilder
            response = ResponseBuilder.error("An error occurred. Please try again.")
            await self.client.send_message(
                chat_id=update.effective_user.id,
                msg=response['text']
            )
