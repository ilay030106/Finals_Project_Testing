"""Legacy config file - maintained for backward compatibility
New code should use config.settings and config.menus instead
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Telegram Bot Configuration (legacy)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Import new menu system
