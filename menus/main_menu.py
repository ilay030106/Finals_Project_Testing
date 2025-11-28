"""Unified menu classes - each menu owns its definition and handlers"""
from telegram import Update
from telegram.ext import ContextTypes
from menus.base_menu import BaseMenu
from utils.response_builder import ResponseBuilder
import logging
from constants.main_menu_constants import MainMenuFields 
from constants.response_fields import ResponseFields
from utils.callback_registry import CallbackRegistry
logger = logging.getLogger(__name__)


class MainMenu(BaseMenu):
    """Unified main menu - contains menu definition"""
    
    def __init__(self, client):
        """Initialize main menu with definition
        
        Args:
            client: TelegramClient instance
        """
        # Pass title and button structure to BaseMenu
        super().__init__(
            client,
            MainMenuFields.TITLE,
            [
                [MainMenuFields.MONITOR_AND_STATUS, MainMenuFields.TRAINING_CONTROL],
                [MainMenuFields.REPORT_AND_VISUAL, MainMenuFields.SETTINGS]
            ]
        )


# Standalone handler functions with explicit dependencies
@CallbackRegistry.register(MainMenuFields.REPORT_AND_VISUAL)
async def handle_reports(update: Update, context: ContextTypes.DEFAULT_TYPE, client, **kwargs) -> None:
    """Handle reporting and visualization button
    
    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        **kwargs: Additional dependencies
    """
    logger.info(f"User {update.effective_user.id} requested reports")
    response = ResponseBuilder.info("You Pressed Button: Reporting And Visualization")
    await client.send_message(msg=response[ResponseFields.TEXT])


@CallbackRegistry.register(MainMenuFields.SETTINGS)
async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE, client, **kwargs) -> None:
    """Handle settings button
    
    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        **kwargs: Additional dependencies
    """
    logger.info(f"User {update.effective_user.id} accessed settings")
    response = ResponseBuilder.info("You Pressed Button: Settings")
    await client.send_message(msg=response[ResponseFields.TEXT])


@CallbackRegistry.register(MainMenuFields.MONITOR_AND_STATUS)
async def handle_monitor_status(update: Update, context: ContextTypes.DEFAULT_TYPE, client, **kwargs) -> None:
    """Handle monitoring and status button
    
    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        **kwargs: Additional dependencies (e.g., monitor service)
    """
    logger.info(f"User {update.effective_user.id} requested monitoring")
    response = ResponseBuilder.info("You Pressed Button: Monitoring And Status")
    await client.send_message(msg=response[ResponseFields.TEXT])



@CallbackRegistry.register(MainMenuFields.TRAINING_CONTROL)
async def handle_train_control(update: Update, context: ContextTypes.DEFAULT_TYPE, client, **kwargs) -> None:
    """Handle training control button
    
    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        **kwargs: Additional dependencies (e.g., trainer, model)
    """
    logger.info(f"User {update.effective_user.id} accessed training control")
    response = ResponseBuilder.info("You Pressed Button: Training Control")
    await client.send_message(msg=response[ResponseFields.TEXT])
    # Future: trainer = kwargs.get('trainer')
    # await trainer.start_training()
