import re
from typing import Union, Iterable, Callable, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def callback_data_format(
    text: str, 
    patterns: Iterable[str]=None, 
    to_remove: Iterable[str]=None
) -> str:
    """Convert text to callback_data format (lowercase with replacements)"""
    if patterns:
        replace_regex = "|".join(map(re.escape, patterns))
        text = re.sub(replace_regex, "_", text)

    if to_remove:
        remove_regex = "|".join(map(re.escape, to_remove))
        text = re.sub(remove_regex, "", text)

    return text.lower()

def find_callback_data_from_menu(identifier, menu_buttons, patterns=None, to_remove=None):
    """Find callback_data from button label or return callback_data as-is
    
    Args:
        identifier: Either a button label or callback_data string
        menu_buttons: The buttons list from menu config (e.g., MAIN_MENU['buttons'])
        patterns: Optional list of patterns to replace with underscore
        to_remove: Optional list of patterns to remove
    
    Returns:
        The callback_data string
    """
    # Look through all buttons in the menu
    for row in menu_buttons:
        for button in row:
            if isinstance(button, (tuple, list)) and len(button) == 2:
                label, data = button
                # If identifier matches the label, return the data
                if identifier == label:
                    return data
                # If identifier matches the data, return it
                if identifier == data:
                    return data
    
    # Not found in menu, convert it to callback_data format with custom patterns
    return callback_data_format(identifier, patterns=patterns, to_remove=to_remove)

def make_button(btn, patterns=None, to_remove=None):
    """Create a button tuple (text, callback_data) from various input formats
    
    Args:
        btn: Either a tuple/list of (text, callback_data) or a single string
        patterns: Optional list of patterns to replace with underscore in callback_data
        to_remove: Optional list of patterns to remove from callback_data
    
    Returns:
        Tuple of (text, callback_data)
    """
    if isinstance(btn, (tuple, list)) and len(btn) == 2:
        return btn
    return (str(btn), callback_data_format(str(btn), patterns=patterns, to_remove=to_remove))

def callback_handler(identifier, menu=None, patterns=None, to_remove=None):
    """Decorator to register callback handlers.
    Pass either callback_data or button label - simplified to use labels directly
    
    Args:
        identifier: Either callback_data string or button label
        menu: Optional Menu object or dict. If None, searches MAIN_MENU.
        patterns: Optional list of patterns to replace with underscore (deprecated)
        to_remove: Optional list of patterns to remove completely (deprecated)
    
    Usage:
        @callback_handler("Reporting And Visualization")  # Auto-finds in MAIN_MENU
        @callback_handler("Settings")  # Auto-finds in MAIN_MENU
        @callback_handler("Back", menu=SETTINGS_MENU)  # Searches in specific menu
    """
    def decorator(func: Callable):
        # Find the actual callback_data
        if menu:
            # Handle both Menu objects and dict formats
            if hasattr(menu, 'get_buttons'):
                # New Menu object
                menu_buttons = menu.get_buttons()
            else:
                # Old dict format
                menu_buttons = menu.get('buttons', [])
            
            callback_data = find_callback_data_from_menu(
                identifier, 
                menu_buttons, 
                patterns=patterns, 
                to_remove=to_remove
            )
        else:
            # Try to import and search in MAIN_MENU
            try:
                from config.menus import MAIN_MENU
                menu_buttons = MAIN_MENU.get_buttons()
                callback_data = find_callback_data_from_menu(
                    identifier, 
                    menu_buttons,
                    patterns=patterns,
                    to_remove=to_remove
                )
            except (ImportError, AttributeError, KeyError) as e:
                logger.warning(f"Could not find menu, using identifier as callback_data: {e}")
                # If no menu found, use identifier directly or format it
                callback_data = callback_data_format(identifier, patterns=patterns, to_remove=to_remove) if (patterns or to_remove) else identifier
        
        # Attach callback_data to the function so we can find it later
        func._callback_data = callback_data
        logger.debug(f"Registered callback: '{identifier}' -> '{callback_data}'")
        return func
    return decorator

