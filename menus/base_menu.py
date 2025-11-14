
from menus.base_handler import BaseHandler
from menus import Menu
from utils.response_builder import ResponseBuilder
from TelegramClient import TelegramClient
from telegram.constants import ParseMode

class BaseMenu(BaseHandler):
    def __init__(self, client,title,rows=None):
        """Initialize main menu with definition and handlers
        
        Args:
            client: TelegramClient instance
        """
        super().__init__(client)
        
        # Define menu structure
        self.menu = Menu(title)
        if rows:
            for row in rows:
                self.menu.add_row(row)
        self.menu.validate()

        # Register handlers
        self._register_callbacks() 
    
    def add_row(self,row):
        """Adding a Buttons row after initialization"""
        self.menu.add_row(row)
        self.menu.validate()

    async def show(self, chat_id: int = None, parse_mode: str = ParseMode.HTML):
        """Display this menu
        
        Args:
            chat_id: Chat ID to send to (uses app_context if None)
            parse_mode: Parse mode for message
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