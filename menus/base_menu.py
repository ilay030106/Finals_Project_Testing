
from menus import Menu
from utils.response_builder import ResponseBuilder
from TelegramClient import TelegramClient
from telegram.constants import ParseMode
from constants.response_fields import ResponseFields
from telegram import Update
from telegram.ext import ContextTypes
import logging
logger = logging.getLogger(__name__)

class BaseMenu:
    """Base class for all menus - provides menu setup and display functionality.
    """
    
    def __init__(self, client, title, rows=None):
        """Initialize menu with definition and handlers
        
        Args:
            client: TelegramClient instance
            title: Menu title text
            rows: List of button rows, where each row is a list of button labels
                  Example: [["Button 1", "Button 2"], ["Button 3"]]
        """
        self.client = client
        self.logger = logger
        
        # Define menu structure first
        self.menu = Menu(title)
        if rows:
            for row in rows:
                self.menu.add_row(row)

        self.menu.validate_structure()


        
        
        
    
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception) -> None:
        """Handle errors in a consistent way
        
        Args:
            update: The update that caused the error
            context: The context object
            error: The exception that was raised
        """
        self.logger.error(f"Error in handler: {error}", exc_info=True)
        
        if update and update.effective_user:
            from utils.response_builder import ResponseBuilder
            response = ResponseBuilder.error("An error occurred. Please try again.")
            await self.client.send_message(
                chat_id=update.effective_user.id,
                msg=response[ResponseFields.TEXT]
            )
    def add_row_to_keyboard(self, row):
        """Add a button row after initialization
        
        Args:
            row: List of button labels for the row
        """
        self.menu.add_row(row)
        self.menu.validate_structure()

    async def show_menu(self, chat_id: int = None, parse_mode: str = ParseMode.HTML):
        """Display this menu
        
        Args:
            chat_id: Chat ID to send to (uses app_context if None)
            parse_mode: Parse mode for message (default: HTML)
        """
        reply_markup = TelegramClient.inline_kb(self.menu.get_buttons())
        response = ResponseBuilder.menu(
            title=self.menu.title,
            keyboard=reply_markup,
            parse_mode=parse_mode
        )
        
        await self.client.send_message(
            chat_id=chat_id,
            msg=response[ResponseFields.TEXT],
            reply_markup=response[ResponseFields.KEYBOARD],
            parse_mode=response[ResponseFields.PARSE_MODE]
        )
