"""Main menu handler - entry point for menu navigation"""
from telegram import Update
from telegram.ext import ContextTypes
from handlers.base_handler import BaseHandler
from utils.telegram_client_utils import callback_handler
from utils.response_builder import ResponseBuilder
import logging

logger = logging.getLogger(__name__)


class MainMenuHandler(BaseHandler):
    """Handler for main menu - delegates to specific menu handlers"""
    
    def __init__(self, client):
        """Initialize main menu handler
        
        Args:
            client: TelegramClient instance
        """
        super().__init__(client)
        self._register_callbacks()
    
    @callback_handler("Reporting And Visualization")
    async def handle_reports(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle reports button - delegates to ReportingMenuHandler
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} requested reports")
        response = ResponseBuilder.info("You Pressed Button: Reporting And Visualization")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler("Settings")
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle settings button - delegates to SettingsMenuHandler
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} accessed settings")
        response = ResponseBuilder.info("You Pressed Button: Settings")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler("Monitoring And Status")
    async def handle_monitor_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle monitoring button - delegates to MonitoringMenuHandler
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} requested monitoring")
        response = ResponseBuilder.info("You Pressed Button: Monitoring And Status")
        await self.client.send_message(msg=response['text'])
    
    @callback_handler("Training Control")
    async def handle_train_control(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle training button - delegates to TrainingMenuHandler
        
        Args:
            update: The update object from Telegram
            context: The context object
        """
        logger.info(f"User {update.effective_user.id} accessed training control")
        response = ResponseBuilder.info("You Pressed Button: Training Control")
        await self.client.send_message(msg=response['text'])


# Backward compatibility alias
MenuHandlers = MainMenuHandler
