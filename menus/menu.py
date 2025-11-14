"""Menu builder system for creating structured inline keyboards"""
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MenuButton:
    """Represents a single button in a menu
    
    Attributes:
        label: The text displayed on the button
        callback_data: The data sent when button is clicked
    """
    label: str
    callback_data: str
    
    def to_tuple(self) -> Tuple[str, str]:
        """Convert button to tuple format for telegram client
        
        Returns:
            Tuple of (label, callback_data)
        """
        return (self.label, self.callback_data)
    
    def __repr__(self) -> str:
        return f"MenuButton(label='{self.label}', callback_data='{self.callback_data}')"


class Menu:
    """Builder class for creating structured menus with validation"""
    
    def __init__(self, title: str):
        """Initialize menu with a title
        
        Args:
            title: The menu title/message to display
        """
        self.title = title
        self.rows: List[List[MenuButton]] = []
        self.logger = logger
    
    def add_button(self, label: str, callback_data: Optional[str] = None) -> 'Menu':
        """Add a single button as a new row
        
        Args:
            label: The button text
            callback_data: Optional callback data (if None, uses label directly)
            
        Returns:
            Self for method chaining
        """
        if callback_data is None:
            callback_data = label
        
        button = MenuButton(label, callback_data)
        self.rows.append([button])
        self.logger.debug(f"Added button: {button}")
        return self
    
    def add_row(self, buttons: List[Union[MenuButton, Tuple[str, str], str]]) -> 'Menu':
        """Add a row of buttons
        
        Args:
            buttons: List of MenuButton objects, (label, callback_data) tuples, or label strings
            
        Returns:
            Self for method chaining
        """
        row = []
        for btn in buttons:
            if isinstance(btn, MenuButton):
                row.append(btn)
            elif isinstance(btn, (tuple, list)) and len(btn) == 2:
                row.append(MenuButton(btn[0], btn[1]))
            elif isinstance(btn, str):
                # Use label directly as callback_data
                row.append(MenuButton(btn, btn))
            else:
                raise ValueError(f"Invalid button format: {btn}")
        
        self.rows.append(row)
        self.logger.debug(f"Added row with {len(row)} buttons")
        return self
    
    def get_buttons(self) -> List[List[Tuple[str, str]]]:
        """Get buttons in format compatible with TelegramClient
        
        Returns:
            List of rows, each containing button tuples
        """
        return [[btn.to_tuple() for btn in row] for row in self.rows]
    
    def to_dict(self) -> dict:
        """Convert menu to dictionary format (legacy compatibility)
        
        Returns:
            Dictionary with 'title' and 'buttons' keys
        """
        return {
            'title': self.title,
            'buttons': self.get_buttons()
        }
    
    def validate(self) -> bool:
        """Validate menu structure
        
        Returns:
            True if valid, raises ValueError if invalid
        """
        if not self.title:
            raise ValueError("Menu must have a title")
        
        if not self.rows:
            raise ValueError("Menu must have at least one button")
        
        # Check for duplicate callback_data
        callback_data_set = set()
        for row in self.rows:
            for btn in row:
                if btn.callback_data in callback_data_set:
                    self.logger.warning(f"Duplicate callback_data found: {btn.callback_data}")
                callback_data_set.add(btn.callback_data)
        
        return True
    
    def __repr__(self) -> str:
        return f"Menu(title='{self.title}', rows={len(self.rows)})"
