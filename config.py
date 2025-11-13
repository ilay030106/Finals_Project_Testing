import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Time zone setting

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

MAIN_MENU={
    "title" : "Welcome To The Control Center!\n\n Please Choose your Action",
    "buttons":[
        [
         ("Monitoring And Status","monitor_and_status"),
         ("Training Control","train_control") 
         ],

         [
         ("Reporting And Visualization","reports"),
         ("Settings","settings"),
         ]
    ]
}