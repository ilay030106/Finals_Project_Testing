from enum import StrEnum


class MainClientConstants(StrEnum):

    class MSGS(StrEnum):
        INIT_SUCCESS_MSG="MainClient initialized successfully"
        ON_ERROR_MSG="An error occurred. Please try again or contact support."
        CALLBACK_REQUEST_ERROR="Failed to process your request."
        RUNNING_MSG="Bot is running. Press Ctrl+C to stop."



    START="start"
    START_DESC="Start the bot and show main menu"
    HELP="help"
    HELP_DESC="Show available commands"
    DIVIDER="="*50
    NO_USERNAME="No username"
    NO_NAME="No name"