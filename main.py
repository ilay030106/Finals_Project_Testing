"""Main bot application with improved architecture"""
from TelegramClient import TelegramClient
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram import Update
from config.settings import get_settings
from app_context import app_context
from menus.main_menu import MainMenu
from utils.logging_config import setup_logging
from utils.response_builder import ResponseBuilder
from utils.command_registry import CommandRegistry, command_handler
from constants.main_client_constants import MainClientConstants
from constants.response_fields import ResponseFields
from constants.app_context_fields import AppContextFields
import logging
from utils.callback_registry import CallbackRegistry
# Initialize settings and logging
settings = get_settings()
setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file
)
logger = logging.getLogger(__name__)


class MainClient:
    """Main bot client with handler coordination"""
    
    def __init__(self):
        """Initialize the main bot client"""
        self.settings = settings
        self.client = TelegramClient()
        self.command_registry = CommandRegistry()
        
        self.main_menu = MainMenu(self.client)
        
        # Store in app_context for handlers to access
        app_context[AppContextFields.CLIENT] = self.client
        app_context[AppContextFields.MAIN_MENU] = self.main_menu
        
        # Register commands
        self._register_commands()
        
        # Register telegram handlers
        self.client.add_text_handler(self.on_text)
        self.client.add_error_handler(self.on_error)
        self.client.add_callback_query_handler(self.on_callback)
        
        logger.info(MainClientConstants.MSGS.INIT_SUCCESS_MSG)
    
    def _register_commands(self) -> None:
        """Register all command handlers"""
        # Auto-register decorated commands
        self.command_registry.auto_register_from_instance(self)
        
        # Register commands with telegram client
        for cmd, info in self.command_registry.get_all_commands().items():
            self.client.add_command_handler(cmd, info['handler'])
        
        logger.info(f"Registered {len(self.command_registry.commands)} commands")
    
    @command_handler(MainClientConstants.START, description=MainClientConstants.START_DESC)
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - send main menu
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username or MainClientConstants.NO_USERNAME
        first_name = update.effective_user.first_name or MainClientConstants.NO_NAME
        
        # Store user info in app_context
        app_context[AppContextFields.USER_ID] = user_id
        app_context[AppContextFields.USER_NAME] = username
        
        logger.info(f"User started bot: {user_id} - {username} - {first_name}")
        
        # Show main menu using unified menu class
        await self.main_menu.show_menu(chat_id=user_id)
    
    @command_handler(MainClientConstants.HELP, description=MainClientConstants.HELP_DESC)
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command - show available commands
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        if not update.effective_user:
            return
        
        help_text = self.command_registry.generate_help_text()
        response = ResponseBuilder.info(help_text)
        
        await self.client.send_message(
            chat_id=update.effective_user.id,
            msg=response[ResponseFields.TEXT]
        )
    
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        text = update.message.text or ""
        
        logger.debug(f"Received text from {user_id}: {text}")
        
        # Echo the message back
        response = ResponseBuilder.custom(f"You said: {text}", emoji="💬")
        await self.client.send_message(
            chat_id=user_id,
            msg=response[ResponseFields.TEXT]
        )
    
    async def on_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        error = context.error
        logger.error(f"Error occurred: {error}", exc_info=True)
        
        if update and update.effective_user:
            response = ResponseBuilder.error(MainClientConstants.MSGS.ON_ERROR_MSG)
            try:
                await self.client.send_message(
                    chat_id=update.effective_user.id,
                    msg=response[ResponseFields.TEXT]
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
    
    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle Button Callback using a Centralized Callback Registry
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        query = update.callback_query
        
        if not query or not update.effective_user:
            return
        
        await query.answer()
        callback_data = query.data
        user_id = update.effective_user.id
        
        logger.debug(f"Callback from user {user_id}: '{callback_data}'")
        
        try:
            # Pass dependencies explicitly to handlers
            found, result = await CallbackRegistry.dispatch(
                update, 
                context,
                client=self.client,
                main_menu=self.main_menu
            )
            
            if not found:
              logger.warning(f"No handler registered for callback_data: '{callback_data}'")
              response = ResponseBuilder.warning(f"Unknown button: {callback_data}")
              await self.client.send_message(msg=response[ResponseFields.TEXT])
        
        except Exception as e:
            logger.error(f"Error in callback handler for '{callback_data}': {e}", exc_info=True)
            response = ResponseBuilder.error(MainClientConstants.MSGS.CALLBACK_REQUEST_ERROR)
            await self.client.send_message(msg=response[ResponseFields.TEXT])


if __name__ == "__main__":
    logger.info(MainClientConstants.DIVIDER)
    logger.info("Starting Telegram Bot...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(MainClientConstants.DIVIDER)
    
    main_client = MainClient()
    
    logger.info(MainClientConstants.MSGS.RUNNING_MSG)
    main_client.client.run_polling(drop_pending_updates=True)