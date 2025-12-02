"""Start command handler"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.new_command_registry import CommandRegistry
import logging

logger = logging.getLogger(__name__)


@CommandRegistry.register("start", description="Start the bot and show main menu")
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> None:
    """Handle /start command - show main menu
    
    Args:
        update: Telegram update
        context: Telegram context
        **kwargs: Dependencies (main_menu, client)
    """
    main_menu = kwargs.get('main_menu')
    
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "User"
    
    logger.info(f"User started bot: {user_id} - {first_name}")
    
    # Show main menu
    if main_menu:
        await main_menu.show_menu(chat_id=user_id)
