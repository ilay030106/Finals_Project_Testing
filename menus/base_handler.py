"""Base handler class for callback registration"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


class BaseHandler:
    """Base class for automatic callback handler registration.
    
    This class provides the mechanism to automatically register callback handlers.
    When your menu class is instantiated, this scans all methods for the 
    @callback_handler decorator and registers them in app_context.
    
    Usage:
        class MyMenu(BaseHandler):
            def __init__(self, client):
                super().__init__(client)
                # Handlers are now registered automatically
            
            @callback_handler("my_button")
            async def handle_my_button(self, update, context):
                pass
    """
    
    def __init__(self, client):
        """Initialize handler with telegram client
        
        Args:
            client: TelegramClient instance
        """
        self.client = client
        self.logger = logger
        
        # Automatically register all decorated callback handlers
        self._register_callbacks()
    
    def _register_callbacks(self) -> None:
        """Register all decorated callback handlers in app_context.
        
        This method scans the instance for methods decorated with @callback_handler
        and registers them in the global app_context registry.
        
        Flow:
            1. Loop through all attributes of the instance
            2. Check if attribute is a callable method
            3. Check if method has '_callback_data' attribute (added by decorator)
            4. Register the method in app_context with its callback_data as key
        """
        from app_context import app_context
        
        # Scan all methods in this instance
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            
            # Check if it's a callable method with callback_data attached
            if callable(attr) and hasattr(attr, '_callback_data'):
                callback_data = attr._callback_data
                
                # Register in global app_context
                app_context.register_callback(callback_data, attr)
                
                self.logger.debug(
                    f"Registered: {self.__class__.__name__}.{attr_name}() "
                    f"-> callback_data='{callback_data}'"
                )
    
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
