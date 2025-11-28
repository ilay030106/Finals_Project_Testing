# Quick Reference Guide

## Project Structure

```
Finals_Project_Testing/
├── main.py                      # Application entry point with MainClient
├── TelegramClient.py            # Telegram API wrapper (singleton)
├── app_context.py               # Global context for user state
├── config/
│   ├── settings.py             # Environment-based configuration
│   └── __init__.py
├── constants/
│   ├── main_client_constants.py
│   ├── main_menu_constants.py
│   ├── telegram_client_constants.py
│   ├── response_fields.py      # Response dict field constants
│   ├── app_context_fields.py   # App context field constants
│   └── __init__.py
├── menus/
│   ├── base_menu.py            # Base class for menu structure
│   ├── menu.py                 # Menu builder classes
│   ├── main_menu.py            # Main menu definition + handlers
│   └── __init__.py
├── utils/
│   ├── callback_registry.py    # Callback handler registry with DI
│   ├── command_registry.py     # Command handler registry
│   ├── response_builder.py     # Consistent response formatting
│   ├── logging_config.py       # Logging configuration
│   └── telegram_client_utils.py
└──
```

---

## Common Tasks

### Add a New Button Handler

Create a standalone function in the appropriate menu file:

```python
# In menus/main_menu.py

@CallbackRegistry.register(MainMenuFields.NEW_BUTTON)
async def handle_new_button(update: Update, context: ContextTypes.DEFAULT_TYPE, client, **kwargs) -> None:
    """Handle new button click

    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        **kwargs: Additional dependencies
    """
    logger.info(f"User {update.effective_user.id} clicked new button")
    response = ResponseBuilder.success("Button clicked!")
    await client.send_message(msg=response[ResponseFields.TEXT])
```

**Important**:

- Handlers are **standalone functions**, not methods
- Dependencies are **injected** via parameters
- Use `@CallbackRegistry.register()` decorator
- Add button to menu structure in `MainMenu.__init__`

---

### Add a New Command

```python
# In main.py (MainClient class)

@command_handler("stats", description="Show bot statistics")
async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show statistics"""
    user_id = update.effective_user.id
    response = ResponseBuilder.info(f"Bot statistics for user: {user_id}")
    await self.client.send_message(
        chat_id=user_id,
        msg=response[ResponseFields.TEXT]
    )
```

**Note**: Commands are still instance methods of `MainClient`

---

### Create a New Menu

```python
# 1. Create constants file: constants/training_menu_constants.py

from enum import StrEnum

class TrainingMenuFields(StrEnum):
    TITLE = "🏋️ Training Control Center"
    START_TRAINING = "Start Training"
    STOP_TRAINING = "Stop Training"
    VIEW_PROGRESS = "View Progress"
    BACK_TO_MAIN = "Back to Main"


# 2. Create menu class: menus/training_menu.py

from telegram import Update
from telegram.ext import ContextTypes
from menus.base_menu import BaseMenu
from utils.response_builder import ResponseBuilder
from utils.callback_registry import CallbackRegistry
from constants.training_menu_constants import TrainingMenuFields
from constants.response_fields import ResponseFields
import logging

logger = logging.getLogger(__name__)


class TrainingMenu(BaseMenu):
    """Training control menu"""

    def __init__(self, client):
        super().__init__(
            client,
            TrainingMenuFields.TITLE,
            [
                [TrainingMenuFields.START_TRAINING, TrainingMenuFields.STOP_TRAINING],
                [TrainingMenuFields.VIEW_PROGRESS],
                [TrainingMenuFields.BACK_TO_MAIN]
            ]
        )


# 3. Add handlers as standalone functions (outside the class)

@CallbackRegistry.register(TrainingMenuFields.START_TRAINING)
async def handle_start_training(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                client, trainer=None, **kwargs) -> None:
    """Handle start training button

    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        trainer: ModelTrainer instance (injected, optional)
        **kwargs: Additional dependencies
    """
    logger.info(f"User {update.effective_user.id} started training")

    # Future ML integration:
    # if trainer:
    #     await trainer.start_training()

    response = ResponseBuilder.success("Training started successfully!")
    await client.send_message(msg=response[ResponseFields.TEXT])


@CallbackRegistry.register(TrainingMenuFields.STOP_TRAINING)
async def handle_stop_training(update: Update, context: ContextTypes.DEFAULT_TYPE,
                               client, trainer=None, **kwargs) -> None:
    """Handle stop training button"""
    logger.info(f"User {update.effective_user.id} stopped training")
    response = ResponseBuilder.warning("Training stopped")
    await client.send_message(msg=response[ResponseFields.TEXT])


@CallbackRegistry.register(TrainingMenuFields.VIEW_PROGRESS)
async def handle_view_progress(update: Update, context: ContextTypes.DEFAULT_TYPE,
                               client, monitor=None, **kwargs) -> None:
    """Handle view progress button"""
    # Future: progress = await monitor.get_progress()
    progress = "Training Progress: 75% complete"
    response = ResponseBuilder.info(progress)
    await client.send_message(msg=response[ResponseFields.TEXT])


@CallbackRegistry.register(TrainingMenuFields.BACK_TO_MAIN)
async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              client, main_menu, **kwargs) -> None:
    """Navigate back to main menu"""
    await main_menu.show_menu(chat_id=update.effective_user.id)


# 4. Register in main.py

class MainClient:
    def __init__(self):
        self.client = TelegramClient()
        self.main_menu = MainMenu(self.client)
        self.training_menu = TrainingMenu(self.client)  # ← Add this

        # Store in app_context
        app_context[AppContextFields.CLIENT] = self.client
        app_context[AppContextFields.MAIN_MENU] = self.main_menu
        app_context[AppContextFields.TRAINING_MENU] = self.training_menu  # ← Add this
```

---

### Use App Context

```python
from app_context import app_context
from constants.app_context_fields import AppContextFields

# Store data
app_context[AppContextFields.USER_ID] = user_id
app_context[AppContextFields.USER_NAME] = username
app_context[AppContextFields.CLIENT] = self.client

# Retrieve data
user_id = app_context[AppContextFields.USER_ID]
client = app_context.get(AppContextFields.CLIENT)

# Clear
app_context.clear()
```

---

### Send Different Response Types

```python
from utils.response_builder import ResponseBuilder
from constants.response_fields import ResponseFields

# Success
response = ResponseBuilder.success("Operation completed!")
await client.send_message(msg=response[ResponseFields.TEXT])

# Error
response = ResponseBuilder.error("Something went wrong")
await client.send_message(msg=response[ResponseFields.TEXT])

# Info
response = ResponseBuilder.info("Here's some information")
await client.send_message(msg=response[ResponseFields.TEXT])

# Warning
response = ResponseBuilder.warning("Please be careful")
await client.send_message(msg=response[ResponseFields.TEXT])

# Custom
response = ResponseBuilder.custom("Custom message", emoji="🎉")
await client.send_message(
    msg=response[ResponseFields.TEXT],
    reply_markup=response[ResponseFields.KEYBOARD],
    parse_mode=response[ResponseFields.PARSE_MODE]
)

# Menu
response = ResponseBuilder.menu(
    title="Choose an option",
    keyboard=inline_keyboard,
    parse_mode='HTML'
)
await client.send_message(
    msg=response[ResponseFields.TEXT],
    reply_markup=response[ResponseFields.KEYBOARD],
    parse_mode=response[ResponseFields.PARSE_MODE]
)
```

---

### Access Settings

```python
from config.settings import get_settings

settings = get_settings()

# Access properties
token = settings.telegram_bot_token
debug_mode = settings.debug
log_level = settings.log_level

# Helper methods
if settings.is_production():
    # Production-specific code
    pass

if settings.is_development():
    # Development-specific code
    pass
```

---

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)  # Include stack trace
```

---

## Configuration (.env file)

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional
DEBUG=true
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
ENVIRONMENT=development
APP_NAME=My Telegram Bot
```

---

## Decorator Patterns

### Callback Handler Registration

```python
from utils.callback_registry import CallbackRegistry

# Basic registration
@CallbackRegistry.register("Button Label")
async def handle_button(update, context, client, **kwargs):
    await client.send_message(msg="Clicked!")

# With constants
from constants.main_menu_constants import MainMenuFields

@CallbackRegistry.register(MainMenuFields.SETTINGS)
async def handle_settings(update, context, client, **kwargs):
    await client.send_message(msg="Settings")
```

### Pattern Matching (Advanced)

```python
# Dynamic callback data with regex
@CallbackRegistry.register_pattern(r"page_(\d+)")
async def handle_pagination(update, context, client, page_num, **kwargs):
    """page_num is extracted from callback_data like 'page_3'"""
    await client.send_message(msg=f"Showing page {page_num}")
```

### Command Handler

```python
from utils.command_registry import command_handler

@command_handler("mycommand")
async def cmd_mycommand(self, update, context):
    """Basic command"""
    pass

@command_handler("mycommand", description="Help text")
async def cmd_mycommand(self, update, context):
    """Command with description"""
    pass

@command_handler("cmd", aliases=["c", "command"])
async def cmd_shortcut(self, update, context):
    """Command with aliases"""
    pass
```

---

## Handler Function Signatures

### Callback Handlers (Standalone Functions)

```python
async def handler_name(
    update: Update,                      # Required
    context: ContextTypes.DEFAULT_TYPE,  # Required
    client,                              # Injected dependency
    **kwargs                             # Additional dependencies
) -> None:
    """Handler docstring"""
    pass
```

### Command Handlers (Instance Methods)

```python
async def cmd_name(
    self,                                # Instance method
    update: Update,                      # Required
    context: ContextTypes.DEFAULT_TYPE   # Required
) -> None:
    """Command docstring"""
    pass
```

---

## Dependency Injection

### Available in MainClient.on_callback()

```python
# Current dependencies passed to handlers:
await CallbackRegistry.dispatch(
    update,
    context,
    client=self.client,           # Always available
    main_menu=self.main_menu,     # Always available
    # Add more as needed:
    # model=self.model,
    # trainer=self.trainer,
    # monitor=self.monitor
)
```

### Accessing Dependencies in Handlers

```python
@CallbackRegistry.register("Train Model")
async def handle_train_model(update, context, client, trainer=None, model=None, **kwargs):
    """Access only what you need"""
    if trainer and model:
        await trainer.start_training(model)

    response = ResponseBuilder.success("Training started!")
    await client.send_message(msg=response[ResponseFields.TEXT])
```

---

## Response Dictionary Format

All `ResponseBuilder` methods return:

```python
{
    'text': str,                      # Message text (required)
    'keyboard': InlineKeyboardMarkup, # Inline keyboard (optional)
    'parse_mode': str                 # Parse mode (optional)
}
```

Access fields using constants:

```python
from constants.response_fields import ResponseFields

response = ResponseBuilder.info("Message")
text = response[ResponseFields.TEXT]
keyboard = response[ResponseFields.KEYBOARD]
parse_mode = response[ResponseFields.PARSE_MODE]
```

---

## Useful Patterns

### Error Handling in Handlers

```python
@CallbackRegistry.register("Risky Operation")
async def handle_risky_operation(update, context, client, **kwargs):
    try:
        # Your code that might fail
        result = perform_operation()
        response = ResponseBuilder.success(f"Done! Result: {result}")
    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        response = ResponseBuilder.error("Invalid input provided")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        response = ResponseBuilder.error("An unexpected error occurred")

    await client.send_message(msg=response[ResponseFields.TEXT])
```

### Navigate Between Menus

```python
@CallbackRegistry.register("Go to Training")
async def handle_go_to_training(update, context, client, training_menu, **kwargs):
    """Navigate to training menu"""
    await training_menu.show_menu(chat_id=update.effective_user.id)

@CallbackRegistry.register("Back to Main")
async def handle_back_to_main(update, context, client, main_menu, **kwargs):
    """Navigate back to main menu"""
    await main_menu.show_menu(chat_id=update.effective_user.id)
```

### Build Dynamic Menu

```python
from menus import Menu
from TelegramClient import TelegramClient

# Create dynamic menu
menu = Menu("Select Item")

for item in items:
    menu.add_button(f"{item.name}", f"item_{item.id}")

menu.validate_structure()

# Create keyboard
reply_markup = TelegramClient.inline_kb(menu.get_buttons())

# Send
response = ResponseBuilder.menu("Select an item:", keyboard=reply_markup)
await client.send_message(
    msg=response[ResponseFields.TEXT],
    reply_markup=response[ResponseFields.KEYBOARD]
)
```

### Conditional Handler Logic

```python
@CallbackRegistry.register("Smart Button")
async def handle_smart_button(update, context, client, **kwargs):
    user_id = update.effective_user.id

    # Get user-specific data
    user_role = app_context.get(f'user_{user_id}_role', 'guest')

    if user_role == 'admin':
        response = ResponseBuilder.success("Admin action executed!")
    elif user_role == 'user':
        response = ResponseBuilder.info("User action executed")
    else:
        response = ResponseBuilder.warning("Access denied")

    await client.send_message(msg=response[ResponseFields.TEXT])
```

---

## Menu System

### BaseMenu Class

Inherit from `BaseMenu` to create new menus:

```python
class MyMenu(BaseMenu):
    def __init__(self, client):
        super().__init__(
            client,
            "Menu Title",
            [
                ["Button 1", "Button 2"],  # Row 1
                ["Button 3"]               # Row 2
            ]
        )
```

### Menu Methods

```python
# Display menu
await menu.show_menu(chat_id=user_id)

# Add row dynamically
menu.add_row_to_keyboard(["New Button"])

# Error handling
await menu.handle_error(update, context, exception)
```

---

## Constants Usage

### Why Use Constants?

```python
# ❌ Bad - magic strings
@CallbackRegistry.register("Settings")
async def handle_settings(...):
    pass

# ✅ Good - constants
from constants.main_menu_constants import MainMenuFields

@CallbackRegistry.register(MainMenuFields.SETTINGS)
async def handle_settings(...):
    pass
```

**Benefits**:

- No typos
- Easy refactoring
- IDE autocomplete
- Type safety

### Creating Constants

```python
# constants/my_menu_constants.py

from enum import StrEnum

class MyMenuFields(StrEnum):
    TITLE = "My Menu Title"
    BUTTON_ONE = "Button 1"
    BUTTON_TWO = "Button 2"
```

---

## Testing Your Bot

### Run the Bot

```bash
# Using uv
uv run ./main.py

# Or with python
python main.py

# With activated virtual environment
.venv\Scripts\Activate.ps1  # Windows
python main.py
```

### Available Bot Commands

- `/start` - Start bot and show main menu
- `/help` - Show available commands

---

## Adding ML Components (Future)

### Step 1: Create ML Components

```python
# ml/model.py
class YourMLModel:
    def __init__(self):
        # Initialize model
        pass

# ml/trainer.py
class ModelTrainer:
    def __init__(self, model):
        self.model = model

    async def start_training(self):
        # Training logic
        pass
```

### Step 2: Register in MainClient

```python
class MainClient:
    def __init__(self):
        self.client = TelegramClient()
        self.main_menu = MainMenu(self.client)

        # ML Components
        self.model = YourMLModel()
        self.trainer = ModelTrainer(self.model)
        self.monitor = TrainingMonitor()

        # ... rest of init

    async def on_callback(self, update, context):
        found, result = await CallbackRegistry.dispatch(
            update,
            context,
            client=self.client,
            main_menu=self.main_menu,
            model=self.model,         # ← ML dependencies
            trainer=self.trainer,
            monitor=self.monitor
        )
```

### Step 3: Use in Handlers

```python
@CallbackRegistry.register("Start Training")
async def handle_start_training(update, context, client, trainer, model, **kwargs):
    """Handler receives ML components"""
    await trainer.start_training()

    response = ResponseBuilder.success("Training started!")
    await client.send_message(msg=response[ResponseFields.TEXT])
```

---

## Troubleshooting

### Handler Not Called

1. Check registration decorator is present: `@CallbackRegistry.register()`
2. Verify callback_data matches button label exactly
3. Check handler function signature includes `client` and `**kwargs`
4. Ensure module is imported (handlers register when module imports)

### Import Errors

```python
# Circular import issue?
# Solution: Import inside function
async def handle_button(update, context, client, **kwargs):
    from menus.other_menu import OtherMenu
    menu = OtherMenu(client)
```

### Menu Not Showing

1. Check `await menu.show_menu(chat_id=user_id)` is called
2. Verify `chat_id` is valid
3. Check menu structure is valid: `menu.validate_structure()`

### Dependencies Not Available in Handler

1. Check dependency is passed in `MainClient.on_callback()`:
   ```python
   await CallbackRegistry.dispatch(update, context, client=self.client, ...)
   ```
2. Verify handler signature includes parameter:
   ```python
   async def handler(update, context, client, new_dep, **kwargs):
   ```

---

## Best Practices

### ✅ Do

- Use constants for all button labels and callback data
- Include docstrings for all handlers
- Log important user actions
- Handle errors gracefully
- Use type hints in function signatures
- Keep handlers focused and simple
- Test handlers with different scenarios

### ❌ Don't

- Use magic strings for callbacks
- Access `app_context` in handlers (use DI instead)
- Put business logic in menu classes
- Ignore errors silently
- Create circular imports
- Mix async and sync code incorrectly

---

## Next Steps

1. **Add More Menus**: Create `TrainingMenu`, `SettingsMenu`, `ReportsMenu`
2. **Implement ML Integration**: Add model, trainer, monitor dependencies
3. **Add Database**: Integrate database for persistent storage
4. **Write Tests**: Add unit tests for handlers
5. **Add Logging**: Enhance logging for production monitoring
6. **Documentation**: Keep docs updated as you add features

---

## Quick Command Reference

```bash
# Project setup
uv init
uv add python-telegram-bot python-dotenv

# Run
uv run ./main.py

# Virtual environment
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# Dependencies
uv add package_name
uv remove package_name
```

---

## File Templates

### New Handler File

```python
"""Handlers for [Feature] menu"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.callback_registry import CallbackRegistry
from utils.response_builder import ResponseBuilder
from constants.response_fields import ResponseFields
from constants.[menu]_constants import [Menu]Fields
import logging

logger = logging.getLogger(__name__)


@CallbackRegistry.register([Menu]Fields.BUTTON_NAME)
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       client, **kwargs) -> None:
    """Handle button click

    Args:
        update: Telegram update
        context: Telegram context
        client: TelegramClient instance (injected)
        **kwargs: Additional dependencies
    """
    logger.info(f"User {update.effective_user.id} clicked button")
    response = ResponseBuilder.info("Button clicked!")
    await client.send_message(msg=response[ResponseFields.TEXT])
```

### New Menu Class

```python
"""[Feature] menu definition"""
from telegram import Update
from telegram.ext import ContextTypes
from menus.base_menu import BaseMenu
from constants.[menu]_constants import [Menu]Fields


class [Menu]Menu(BaseMenu):
    """[Feature] menu"""

    def __init__(self, client):
        super().__init__(
            client,
            [Menu]Fields.TITLE,
            [
                [[Menu]Fields.BUTTON_1, [Menu]Fields.BUTTON_2],
                [[Menu]Fields.BUTTON_3]
            ]
        )
```

---

## Summary

This reference covers the **dependency injection architecture** where:

- **Handlers are standalone functions** receiving dependencies explicitly
- **CallbackRegistry manages handler registration** via decorators
- **Dependencies are injected** through `dispatch(**dependencies)`
- **Menus define structure**, handlers implement logic
- **Ready for ML integration** with clear dependency paths

For detailed architecture explanations, see `ARCHITECTURE.md`.
