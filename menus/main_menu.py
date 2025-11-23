"""Unified menu classes - each menu owns its definition and handlers"""
from telegram import Update
from telegram.ext import ContextTypes
from menus.base_menu import BaseMenu
from utils.telegram_client_utils import callback_handler
from utils.response_builder import ResponseBuilder
import logging
from constants.main_menu_constants import MainMenuConstants 
logger = logging.getLogger(__name__)


class MainMenu(BaseMenu):
    """Unified main menu - contains menu definition and all handlers"""
    
    def __init__(self, client):
        """Initialize main menu with definition and handlers
        
        Args:
            client: TelegramClient instance
        """
        # Pass title and button structure to BaseMenu
        super().__init__(
            client,
            MainMenuConstants.TITLE,
            [
                [MainMenuConstants.MONITOR_AND_STATUS, MainMenuConstants.TRAINING_CONTROL],
                [MainMenuConstants.REPORT_AND_VISUAL, MainMenuConstants.SETTINGS]
            ]
        )
    
    @callback_handler(MainMenuConstants.REPORT_AND_VISUAL)
    async def handle_reports(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle reporting and visualization button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} requested reports")
        response = ResponseBuilder.info("You Pressed Button: Reporting And Visualization")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler(MainMenuConstants.SETTINGS)
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle settings button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} accessed settings")
        response = ResponseBuilder.info("You Pressed Button: Settings")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler(MainMenuConstants.MONITOR_AND_STATUS)
    async def handle_monitor_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle monitoring and status button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} requested monitoring")
        response = ResponseBuilder.info("You Pressed Button: Monitoring And Status")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler(MainMenuConstants.TRAINING_CONTROL)
    async def handle_train_control(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle training control button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} accessed training control")
        response = ResponseBuilder.info("You Pressed Button: Training Control")
        await self.client.send_message(msg=response['text'])


# Backward compatibility aliases
MainMenuHandler = MainMenu
MenuHandlers = MainMenu
