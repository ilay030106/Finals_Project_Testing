from TelegramClient import TelegramClient
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram import Update
from config import DEBUG,MAIN_MENU
from app_context import app_context

class MainClient:
    def __init__(self):
        self.client = TelegramClient()
        self.client.add_command_handler("start", self.cmd_start)
        self.client.add_text_handler(self.on_text)
        self.client.add_error_handler(self.on_error)
        self.client.add_callback_query_handler(self.on_callback)
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - send a welcome message with inline keyboard"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        username = update.effective_user.username or "No username"
        first_name = update.effective_user.first_name or "No name"
        
        app_context['user_id'] = user_id
        app_context['username'] = username
        
        if DEBUG:
            print(f"User started bot: {user_id} - {username} - {first_name}")
        

        reply_markup = TelegramClient.inline_kb(MAIN_MENU['buttons'])
        
        welcome_msg = MAIN_MENU['title']
        
        await self.client.send_message(
            msg=welcome_msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        text = update.message.text or ""
        
        if DEBUG:
            print(f"Received text from {user_id}: {text}")
        
        # Echo the message back
        await self.client.send_message(
            chat_id=user_id,
            msg=f"You said: {text}",
            reply_markup=None,
            parse_mode=None
        )
    
    async def on_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        error = context.error
        print(f"Error occurred: {error}")
        if DEBUG and update:
            print(f"Update that caused error: {update}")
    
    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        
        if not query or not update.effective_user:
            return
        
        await query.answer()
        data = query.data
        user_id = update.effective_user.id 
        
        if DEBUG:
            print(f"Callback from {user_id}: {data}")

        match data:
            case "reports":
                await self.client.send_message(
                    msg="You Pressed Button reports",
                )
            case "settings":
                await self.client.send_message(
                    msg="You Pressed Button settings",
                )
            case "monitor_and_status":
                await self.client.send_message(
                    msg="You Pressed Button monitor_and_status",
                )
            case "train_control":
                await self.client.send_message(
                    msg="You Pressed Button train_control",
                )
            case _: 
                await self.client.send_message(
                    msg=f"Unknown button: {data}",
                )


if __name__ == "__main__":
    print("Starting Telegram Bot...")
    main_client = MainClient()
    print("Bot is running. Press Ctrl+C to stop.")
    main_client.client.run_polling(drop_pending_updates=True)