"""Unified menu classes - each menu owns its definition and handlers"""
from telegram import Update
from telegram.ext import ContextTypes
from menus.base_menu import BaseMenu
from utils.telegram_client_utils import callback_handler
from utils.response_builder import ResponseBuilder
import logging

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
            "Welcome To The Control Center!\n\nPlease Choose your Action",
            [
                ["Monitoring And Status", "Training Control"],
                ["Reporting And Visualization", "Settings"]
            ]
        )
    
    @callback_handler("Reporting And Visualization")
    async def handle_reports(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle reporting and visualization button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} requested reports")
        response = ResponseBuilder.info("You Pressed Button: Reporting And Visualization")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler("Settings")
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle settings button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} accessed settings")
        response = ResponseBuilder.info("You Pressed Button: Settings")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler("Monitoring And Status")
    async def handle_monitor_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle monitoring and status button
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} requested monitoring")
        response = ResponseBuilder.info("You Pressed Button: Monitoring And Status")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler("Training Control")
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
