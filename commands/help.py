"""Help command handler"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.new_command_registry import CommandRegistry
from utils.response_builder import ResponseBuilder
from constants.response_fields import ResponseFields
import logging

logger = logging.getLogger(__name__)


@CommandRegistry.register("help", description="Show available commands and help")
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> None:
    """Handle /help command - show available commands
    
    Args:
        update: Telegram update
        context: Telegram context
        **kwargs: Dependencies (client)
    """
    client = kwargs.get('client')
    
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
