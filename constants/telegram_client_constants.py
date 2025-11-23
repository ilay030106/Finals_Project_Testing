from enum import StrEnum

class TelegramClientConstants(StrEnum):
    BOT_TOKEN_ERROR="Telegram Bot token not found in environment variables"
    CLIENT_INIT_SUCCESS="TelegramClient initialized"