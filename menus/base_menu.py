
from menus.base_handler import BaseHandler
from menus import Menu
from utils.response_builder import ResponseBuilder
from TelegramClient import TelegramClient
from telegram.constants import ParseMode

class BaseMenu(BaseHandler):
    """Base class for all menus - provides menu setup and display functionality.
    
    This class combines menu structure definition with automatic handler registration.
    
    Usage:
        class MyMenu(BaseMenu):
            def __init__(self, client):
                super().__init__(
                    client,
                    "My Menu Title",
                    [
                        ["Button 1", "Button 2"],
                        ["Button 3"]
                    ]
                )
            
            @callback_handler("Button 1")
            async def handle_button1(self, update, context):
                # Handle button 1 click
                pass
    
    The menu buttons use their labels as callback_data by default.
    So a button with label "Button 1" will send callback_data="Button 1".
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
        self.menu.validate()
        
        # Initialize parent (this will call _register_callbacks() automatically)
        super().__init__(client)
    
    def add_row(self, row):
        """Add a button row after initialization
        
        Args:
            row: List of button labels for the row
        """
        self.menu.add_row(row)
        self.menu.validate()

    async def show(self, chat_id: int = None, parse_mode: str = ParseMode.HTML):
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
            msg=response['text'],
            reply_markup=response['keyboard'],
            parse_mode=response['parse_mode']
        )
