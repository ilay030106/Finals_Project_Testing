import logging
from typing import Callable

logger = logging.getLogger(__name__)


def make_button(btn):
    """Create a button tuple (text, callback_data) from various input formats.
    
    Args:
        btn: Either a tuple/list of (text, callback_data) or a single string
    
    Returns:
        Tuple of (text, callback_data)
    """
    if isinstance(btn, (tuple, list)) and len(btn) == 2:
        return btn
    return (str(btn), str(btn))


def callback_handler(callback_data: str):
    """Decorator to bind a method to a callback_data string.
    
    This is a simple decorator that attaches callback_data to a method.
    The method will be automatically registered when the class is instantiated
    (via BaseHandler._register_callbacks()).
    
    Args:
        callback_data: The exact callback_data string that Telegram will send.
                      This should match the button's callback_data exactly.
    
    Usage:
        @callback_handler("Monitoring And Status")
        async def handle_monitoring(self, update, context):
            # This method will be called when user clicks button with
            # callback_data="Monitoring And Status"
            pass
    
    How it works:
        1. You decorate a method with @callback_handler("some_callback_data")
        2. The decorator attaches callback_data to the method as an attribute
        3. When your menu class is instantiated, BaseHandler._register_callbacks()
           scans all methods looking for this attribute
        4. Found methods are registered in app_context
        5. When Telegram sends a callback, on_callback() looks up the handler
           in app_context and executes it
    """
    def decorator(func: Callable):
        # Simply attach the callback_data to the function
        # The BaseHandler will find this attribute and register the handler
        func._callback_data = callback_data
        logger.debug(f"Decorated method '{func.__name__}' with callback_data='{callback_data}'")
        return func
    return decorator

