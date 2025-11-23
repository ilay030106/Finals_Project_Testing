"""Telegram client wrapper with singleton pattern"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, ContextTypes, filters, BaseHandler, CallbackQueryHandler
)
from typing import Iterable, Optional
from config.settings import get_settings
from app_context import app_context
from utils.telegram_client_utils import make_button
from constants.telegram_client_constants import TelegramClientConstants
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramClient:
    _instance = None
    _initialized = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramClient,cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if TelegramClient._initialized:
            return
        
        if not settings.telegram_bot_token:
            raise ValueError(TelegramClientConstants.BOT_TOKEN_ERROR)
        
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        
        self.last_messages = {}
        
        TelegramClient._initialized = True
        logger.info(TelegramClientConstants.CLIENT_INIT_SUCCESS)

    async def send_message(self,msg,chat_id=None,reply_markup=None, parse_mode=None):
        if chat_id is None:
            chat_id = app_context.get('user_id')
        await self.app.bot.send_message(chat_id=chat_id,
                                        text=msg,
                                        reply_markup=reply_markup
                                        ,parse_mode=parse_mode)
        
    def run_polling(self,drop_pending_updates=True):
        self.app.run_polling(drop_pending_updates=drop_pending_updates)

    async def run_polling_async(self, drop_pending_updates = True):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=drop_pending_updates)

    async def stop_polling_async(self):
        """Gracefully stop polling and shutdown the application."""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
    
    def run_webhook(
        self,
        listen = "0.0.0.0",
        port = 8000,
        url_path = "/webhook",
        webhook_url = None,
        secret_token= None,
        drop_pending_updates = True,
    ):
        """
        Run the bot using webhook mode (blocking).

        Provide a public webhook_url (e.g., from reverse proxy) and optional secret_token.
        """
        self.app.run_webhook(
            listen=listen,
            port=port,
            url_path=url_path,
            webhook_url=webhook_url,
            secret_token=secret_token,
            drop_pending_updates=drop_pending_updates,
        )
    
    def add_handler(self, handler):
        """Register any custom handler (ConversationHandler, etc.)."""
        self.app.add_handler(handler)

    def add_text_handler(self,callback,allow_commands=False):
        f=filters.TEXT if allow_commands else (filters.TEXT & ~filters.COMMAND)
        self.app.add_handler(MessageHandler(f,callback))
    
    def add_command_handler(self,command,callback):
        self.app.add_handler(CommandHandler(command,callback))
    
    def add_error_handler(self,callback):
        self.app.add_error_handler(callback)
    
    def add_callback_query_handler(self, callback, pattern = None):
        """Convenience to add a CallbackQueryHandler."""
        self.app.add_handler(CallbackQueryHandler(callback, pattern=pattern))
    
    async def handle_message(self, update, context):
        """Default text handler: store user's last message (no business logic)."""
        if not update.effective_user or not update.message:
            return
        user_id = update.effective_user.id
        text = update.message.text or ""
        self.last_messages[user_id] = text
        
        
    
    @staticmethod
    def inline_btns_row(buttons: Iterable[tuple[str, str]]):
        """Create a row of inline buttons.
        
        Args:
            buttons: Iterable of (label, callback_data) tuples
        
        Returns:
            List of InlineKeyboardButton objects
        """
        return [InlineKeyboardButton(text=text, callback_data=data) 
                for btn in buttons 
                for text, data in [make_button(btn)]]
    
    @staticmethod
    def inline_kb(kb):
        """Create an inline keyboard markup from button rows.
        
        Args:
            kb: List of rows, where each row is a list of (label, callback_data) tuples
        
        Returns:
            InlineKeyboardMarkup object
        """
        return InlineKeyboardMarkup([TelegramClient.inline_btns_row(row) for row in kb]) 