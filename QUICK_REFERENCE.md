# Quick Reference Guide

## Project Structure

```
Finals_Project_Testing/
├── handlers/               # Handler modules
│   ├── base_handler.py    # Base class for all handlers
│   └── menu_handlers.py   # Legacy menu button handlers
├── menus/                  # Unified menu system
│   ├── base_menu.py       # BaseMenu class - common menu functionality
│   ├── base_handler.py    # BaseHandler class - callback registration
│   ├── menu.py            # Menu builder classes
│   └── main_menu.py       # MainMenu class - unified menu + handlers
├── state/                  # State management
│   └── user_session.py    # User sessions
├── config/                 # Configuration
│   ├── settings.py        # Settings management
│   └── menus.py           # Legacy menu definitions (being phased out)
├── utils/                  # Utilities
│   ├── logging_config.py  # Logging setup
│   ├── response_builder.py # Response formatting
│   ├── command_registry.py # Command registration
│   └── telegram_client_utils.py # Telegram helpers
├── TelegramClient.py      # Telegram client wrapper
├── app_context.py         # Global context
├── main.py                # Main application
└── config.py              # Legacy config (backward compat)
```

## Common Tasks

### Add a New Menu Button Handler

```python
# In the appropriate menu class (e.g., menus/main_menu.py)

@callback_handler("New Button")
async def handle_new_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new button click"""
    logger.info(f"User {update.effective_user.id} clicked new button")
    response = ResponseBuilder.success("Button clicked!")
    await self.client.send_message(msg=response['text'])
```

**Note**: Handlers are now part of their respective menu classes. Add the button to the menu's `__init__` rows and implement the handler method in the same class.

### Add a New Command

```python
# In main.py (MainClient class)

@command_handler("stats", description="Show bot statistics")
async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    stats = f"Active sessions: {len(session_manager.get_all_sessions())}"
    response = ResponseBuilder.info(stats)
    await self.client.send_message(
        chat_id=update.effective_user.id,
        msg=response['text']
    )
```

### Create a New Menu (Unified Class Pattern)

```python
# In menus/training_menu.py

from menus.base_menu import BaseMenu
from utils.telegram_client_utils import callback_handler
from utils.response_builder import ResponseBuilder
import logging

logger = logging.getLogger(__name__)

class TrainingMenu(BaseMenu):
    """Training control menu - unified menu definition and handlers"""

    def __init__(self, client):
        """Initialize training menu with definition and handlers

        Args:
            client: TelegramClient instance
        """
        super().__init__(
            client,
            "🏋️ Training Control Center",
            [
                ["Start Training", "Stop Training"],
                ["View Progress", "Training Settings"],
                ["Back to Main"]
            ]
        )

    @callback_handler("Start Training")
    async def handle_start_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle start training button"""
        logger.info(f"User {update.effective_user.id} started training")
        response = ResponseBuilder.success("Training started successfully!")
        await self.client.send_message(msg=response['text'])

    @callback_handler("Stop Training")
    async def handle_stop_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle stop training button"""
        logger.info(f"User {update.effective_user.id} stopped training")
        response = ResponseBuilder.warning("Training stopped")
        await self.client.send_message(msg=response['text'])

    @callback_handler("View Progress")
    async def handle_view_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle view progress button"""
        progress = "Training Progress: 75% complete"
        response = ResponseBuilder.info(progress)
        await self.client.send_message(msg=response['text'])

    @callback_handler("Back to Main")
    async def handle_back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle back to main menu"""
        # Import here to avoid circular imports
        from menus.main_menu import MainMenu

        main_menu = MainMenu(self.client)
        await main_menu.show()

# In main.py - register the new menu
self.training_menu = TrainingMenu(self.client)
```

### Legacy Menu Creation (Separate Definition - Being Phased Out)

```python
# In config/menus.py

# Use labels directly as callback_data (RECOMMENDED)
SETTINGS_MENU = Menu("⚙️ Settings") \
    .add_row(["Language", "Notifications"]) \
    .add_button("Back to Main")
# Results in callback_data: "Language", "Notifications", "Back to Main"

# Or specify callback_data explicitly if needed
SETTINGS_MENU = Menu("⚙️ Settings") \
    .add_button("Language", "lang_setting") \
    .add_button("Notifications", "notif_setting") \
    .add_button("Back to Main", "back_main")

SETTINGS_MENU.validate()
```

### Use User Session

```python
from state.user_session import session_manager

# Get session
session = session_manager.get_session(user_id, username)

# Store data
session.set("preferred_language", "en")
session.set_state("awaiting_report_name")

# Retrieve data
language = session.get("preferred_language", "en")

# Track menu
session.set_menu("SETTINGS_MENU")

# Reset session
session.reset()
```

### Send Different Response Types

```python
from utils.response_builder import ResponseBuilder

# Success
response = ResponseBuilder.success("Operation completed!")

# Error
response = ResponseBuilder.error("Something went wrong")

# Info
response = ResponseBuilder.info("Here's some information")

# Warning
response = ResponseBuilder.warning("Please be careful")

# Custom
response = ResponseBuilder.custom("Custom message", emoji="🎉")

# Menu
response = ResponseBuilder.menu(
    title="Choose an option",
    keyboard=inline_keyboard
)

# Send
await self.client.send_message(
    msg=response['text'],
    reply_markup=response['keyboard'],
    parse_mode=response['parse_mode']
)
```

### Access Settings

```python
from config.settings import get_settings

settings = get_settings()

if settings.debug:
    logger.debug("Debug info")

if settings.is_production():
    # Production-specific code
    pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)  # Include stack trace
```

## Configuration (.env file)

```env
# Required
TELEGRAM_BOT_TOKEN=your_token_here

# Optional
DEBUG=true
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
SESSION_TIMEOUT_HOURS=24
ENVIRONMENT=development
APP_NAME=My Telegram Bot
```

## Decorator Patterns

### Callback Handler

The `@callback_handler` decorator automatically finds the callback_data from menu definitions:

```python
# Simple label matching (RECOMMENDED)
@callback_handler("Monitoring And Status")
# Automatically searches MAIN_MENU for "Monitoring And Status" label
# Extracts its callback_data: "Monitoring And Status"
# Registers handler with that callback_data

# Specific menu
@callback_handler("Back", menu=SETTINGS_MENU)
# Searches in SETTINGS_MENU instead of MAIN_MENU

# Direct callback_data (if using explicit callback_data in menu)
@callback_handler("custom_callback")
# Uses "custom_callback" directly if not found in menus
```

**How it works:**

1. Decorator receives a label (e.g., "Monitoring And Status")
2. Searches in menu (default: MAIN_MENU) for button with that label
3. Extracts the callback_data from that button (e.g., "Monitoring And Status")
4. Attaches callback_data to the handler function
5. BaseHandler.\_register_callbacks() finds all decorated methods and registers them

- `patterns=[" ", "-"]` - Replace these characters with `_`
- `to_remove=["ing", "!"]` - Remove these substrings completely

**Result Examples:**

- `"Monitoring And Status"` + `patterns=[" "]`, `to_remove=["ing"]` → `monitor_and_status`

### Command Handler

```python
@command_handler("command")                          # Basic
@command_handler("command", description="Help text") # With description
@command_handler("cmd", aliases=["c", "command"])    # With aliases
```

## Response Dictionary Format

```python
{
    'text': "Message text",           # Required
    'keyboard': InlineKeyboardMarkup, # Optional
    'parse_mode': 'HTML'             # Optional
}
```

## Useful Patterns

### Error Handling in Handlers

```python
async def handle_something(self, update, context):
    try:
        # Your code
        response = ResponseBuilder.success("Done!")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        response = ResponseBuilder.error("Failed to process")

    await self.client.send_message(msg=response['text'])
```

### Check User Session State

```python
session = session_manager.get_session(user_id)
if session.conversation_state == "awaiting_input":
    # Handle input
    session.set_state(None)  # Clear state
```

### Build Dynamic Menu

```python
menu = Menu("Dynamic Menu")

for item in items:
    menu.add_button(item.name, f"select_{item.id}")

menu.validate()
reply_markup = TelegramClient.inline_kb(menu.get_buttons())
```

## Unified Menu Class Pattern

The project uses a unified architecture where each menu is a class that inherits from `BaseMenu` and contains both the menu definition and its handlers.

### Base Classes

- **BaseHandler**: Provides callback registration functionality
- **BaseMenu**: Extends BaseHandler, provides menu setup and display

### Menu Class Structure

```python
from menus.base_menu import BaseMenu
from utils.telegram_client_utils import callback_handler

class MyMenu(BaseMenu):
    def __init__(self, client):
        # Define menu structure in super().__init__
        super().__init__(
            client,
            "Menu Title",
            [
                ["Button 1", "Button 2"],
                ["Button 3"]
            ]
        )

    @callback_handler("Button 1")
    async def handle_button1(self, update, context):
        # Handler implementation
        pass
```

### Benefits

- **Unified**: Menu definition and handlers in one place
- **Inheritance**: No code duplication
- **Modular**: Easy to create new menus
- **Auto-registration**: Handlers automatically registered
- **Type-safe**: Consistent interface through inheritance

## Testing Commands

```bash
# Start bot
uv run ./main.py

# Or with python
python main.py
```

## Available Commands (in bot)

- `/start` - Start bot and show main menu
- `/help` - Show available commands

## Next Steps

1. Create additional unified menu classes (TrainingMenu, SettingsMenu, ReportsMenu)
2. Implement actual menu navigation logic between menus
3. Add menu summary functionality to BaseMenu
4. Implement conversation flows using session states
5. Add database integration
6. Add tests for menu classes
7. Migrate remaining legacy handlers to unified menu classes
