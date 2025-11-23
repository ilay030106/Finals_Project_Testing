
from menus.base_handler import BaseHandler
from menus import Menu
from utils.response_builder import ResponseBuilder
from TelegramClient import TelegramClient
from telegram.constants import ParseMode
from constants.response_fields import ResponseFields

class BaseMenu(BaseHandler):
    """Base class for all menus - provides menu setup and display functionality.
    
    This class combines menu structure definition with automatic handler registration.
    
    """
    
    def __init__(self, client, title, rows=None):
        """Initialize menu with definition and handlers
        
        Args:
            client: TelegramClient instance
            title: Menu title text
            rows: List of button rows, where each row is a list of button labels
                  Example: [["Button 1", "Button 2"], ["Button 3"]]
        """
        # Define menu structure first
        self.menu = Menu(title)
        if rows:
            for row in rows:
                self.menu.add_row(row)
        self.menu.validate_structure()
        
        # Initialize parent (this will call _register_callbacks() automatically)
        super().__init__(client)
    
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
