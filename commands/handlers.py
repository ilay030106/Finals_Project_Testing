"""All command handlers in one file"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.command_registry import CommandRegistry
from utils.response_builder import ResponseBuilder
from constants.response_fields import ResponseFields
from constants.app_context_fields import AppContextFields
from constants.commands import CommandsFields
from app_context import app_context
import logging

logger = logging.getLogger(__name__)


@CommandRegistry.register(CommandsFields.START, description=CommandsFields.START_DESC)
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> None:
    """Handle /start command - show main menu
    
    Args:
        update: Telegram update
        context: Telegram context
    """
    main_menu = app_context.get(AppContextFields.MAIN_MENU)
    
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "User"
    
    logger.info(f"User started bot: {user_id} - {first_name}")
    
    # Show main menu
    if main_menu:
        await main_menu.show_menu(chat_id=user_id)


@CommandRegistry.register(CommandsFields.HELP, description=CommandsFields.HELP_DESC)
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> None:
    """Handle /help command - show available commands
    
    Args:
        update: Telegram update
        context: Telegram context
    """
    client = app_context.get(AppContextFields.CLIENT)
    
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    
    # Generate help text from registered commands
    help_text = CommandRegistry.generate_help_text()
    response = ResponseBuilder.info(help_text)
    
    logger.info(f"User {user_id} requested help")
    
    # Send help message
    if client:
        await client.send_message(
            chat_id=user_id,
            msg=response[ResponseFields.TEXT]
        )


