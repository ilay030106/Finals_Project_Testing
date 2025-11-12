import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, ContextTypes, filters, BaseHandler, CallbackQueryHandler
)
from config import TELEGRAM_BOT_TOKEN
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
        
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram Bot token not found in env variables")
        
        self.app =Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        self.last_messages= {}
        
        TelegramClient._initialized = True

    async def send_message(self,chat_id,msg,reply_markup,parse_mode):
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
    

