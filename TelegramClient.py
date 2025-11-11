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
    
        