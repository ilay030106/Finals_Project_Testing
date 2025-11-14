"""Main bot application with improved architecture"""
from TelegramClient import TelegramClient
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram import Update
from config.settings import get_settings
from config.menus import MAIN_MENU
from app_context import app_context
from state.user_session import session_manager
from handlers.menu_handlers import MenuHandlers
from utils.logging_config import setup_logging
from utils.response_builder import ResponseBuilder
from utils.command_registry import CommandRegistry, command_handler
import logging

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
        
        # Initialize handlers
        self.menu_handlers = MenuHandlers(self.client)
        
        # Register commands
        self._register_commands()
        
        # Register telegram handlers
        self.client.add_text_handler(self.on_text)
        self.client.add_error_handler(self.on_error)
        self.client.add_callback_query_handler(self.on_callback)
        
        logger.info("MainClient initialized successfully")
    
    def _register_commands(self) -> None:
        """Register all command handlers"""
        # Auto-register decorated commands
        self.command_registry.auto_register_from_instance(self)
        
        # Register commands with telegram client
        for cmd, info in self.command_registry.get_all_commands().items():
            self.client.add_command_handler(cmd, info['handler'])
        
        logger.info(f"Registered {len(self.command_registry.commands)} commands")
    
    @command_handler("start", description="Start the bot and show main menu")
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - send main menu
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username or "No username"
        first_name = update.effective_user.first_name or "No name"
        
        # Get or create user session
        # Each user has their own session
        session = session_manager.get_session(user_id, username)
        session.set_menu("MAIN_MENU")
        
        # Store in app_context for backward compatibility
        app_context['user_id'] = user_id
        app_context['username'] = username
        
        logger.info(f"User started bot: {user_id} - {username} - {first_name}")
        
        # Build and send menu
        reply_markup = TelegramClient.inline_kb(MAIN_MENU.get_buttons())
        response = ResponseBuilder.menu(
            title=MAIN_MENU.title,
            keyboard=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        await self.client.send_message(
            msg=response['text'],
            reply_markup=response['keyboard'],
            parse_mode=response['parse_mode']
        )
    
    @command_handler("help", description="Show available commands")
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
            msg=response['text']
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
        
        # Update session activity
        session = session_manager.get_session(user_id)
        session.update_activity()
        
        logger.debug(f"Received text from {user_id}: {text}")
        
        # Echo the message back
        response = ResponseBuilder.custom(f"You said: {text}", emoji="💬")
        await self.client.send_message(
            chat_id=user_id,
            msg=response['text']
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
            response = ResponseBuilder.error("An error occurred. Please try again or contact support.")
            try:
                await self.client.send_message(
                    chat_id=update.effective_user.id,
                    msg=response['text']
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
    
    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks dynamically using callback registry
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        query = update.callback_query
        
        if not query or not update.effective_user:
            return
        
        await query.answer()
        data = query.data
        user_id = update.effective_user.id
        
        # Update session activity
        session = session_manager.get_session(user_id)
        session.update_activity()
        
        logger.debug(f"Callback from {user_id}: {data}")
        
        # Get handler from app_context registry
        handler = app_context.get_callback_handler(data)
        if handler:
            try:
                await handler(update, context)
            except Exception as e:
                logger.error(f"Error in callback handler for '{data}': {e}", exc_info=True)
                response = ResponseBuilder.error("Failed to process your request.")
                await self.client.send_message(msg=response['text'])
        else:
            logger.warning(f"No handler found for callback: {data}")
            response = ResponseBuilder.warning(f"Unknown button: {data}")
            await self.client.send_message(msg=response['text'])


if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Starting Telegram Bot...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("="*50)
    
    main_client = MainClient()
    
    logger.info("Bot is running. Press Ctrl+C to stop.")
    main_client.client.run_polling(drop_pending_updates=True)