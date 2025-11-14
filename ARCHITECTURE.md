# Project Architecture Improvements - Flow Documentation

## Overview

This document explains the improved architecture and flow of the refactored Telegram bot project.

---

## 1. Handler Module System

### Structure

```
handlers/
├── __init__.py
├── base_handler.py       # Base class with common functionality
└── menu_handlers.py      # Specific menu button handlers
```

### Flow

1. **BaseHandler** provides common functionality:

   - Automatic callback registration via `_register_callbacks()`
   - Error handling helper methods
   - Logger access
   - Reference to TelegramClient

2. **MenuHandlers** extends BaseHandler:
   - Contains all menu button handlers
   - Each handler decorated with `@callback_handler`
   - Auto-registers on initialization
   - Uses ResponseBuilder for consistent formatting

### Benefits

- Separation of concerns
- Easy to add new handler modules (reports_handlers.py, settings_handlers.py, etc.)
- Shared functionality in base class
- Clear organization by feature

---

## 2. Menu Management System

### Structure

```
menus/
├── __init__.py
└── menu.py              # Menu and MenuButton classes

config/
└── menus.py             # Menu definitions
```

### Flow

1. **MenuButton dataclass**:

   - Represents a single button with label and callback_data
   - `to_tuple()` method for telegram compatibility

2. **Menu class** (Builder pattern):

   ```python
   menu = Menu("Title")
       .add_button("Label")  # Uses label as callback_data
       .add_row(["Label1", "Label2"])  # Both labels used as callback_data
   ```

   - Fluent API for building menus
   - **Labels are used directly as callback_data** (no transformation)
   - Optional explicit callback_data: `.add_button("Label", "custom_data")`
   - Validation of menu structure
   - Convert to dict format for backward compatibility

3. **Usage in config/menus.py**:
   ```python
   MAIN_MENU = Menu("Welcome...")
       .add_row(["Monitoring And Status", "Training Control"])
       .add_row(["Reporting And Visualization", "Settings"])
   ```
   - "Monitoring And Status" → `Monitoring And Status`
   - "Training Control" → `Training Control`
   - "Reporting And Visualization" → `Reporting And Visualization`
   - "Settings" → `Settings`

### Benefits

- **Simple and consistent** - Label is the callback_data (no transformation)
- **Easy to understand** - What you see is what you get
- Type-safe menu creation
- Validation catches errors early
- Cleaner syntax than raw dictionaries
- Easy to compose complex menus
- Duplicate callback_data detection

---

## 3. State Management System

### Structure

```
state/
├── __init__.py
└── user_session.py      # UserSession and SessionManager classes
```

### Flow

1. **UserSession** (per user):

   - Stores user_id, username
   - Tracks current_menu and conversation_state
   - Custom data storage (dict)
   - Activity tracking with timestamps

2. **SessionManager** (singleton):

   - Manages all user sessions
   - `get_session(user_id)` - get or create
   - `cleanup_inactive()` - remove old sessions
   - Global instance: `session_manager`

3. **Usage**:

   ```python
   from state.user_session import session_manager

   session = session_manager.get_session(user_id, username)
   session.set_menu("MAIN_MENU")
   session.set("last_report", report_data)
   ```

### Benefits

- Per-user state isolation
- Conversation flow tracking
- Automatic activity tracking
- Session cleanup for memory management
- Easy to extend with custom data

---

## 4. Settings Management

### Structure

```
config/
├── __init__.py
└── settings.py          # Settings class with validation
```

### Flow

1. **Settings class**:

   - Loads from environment variables
   - Type conversion and validation
   - Helper methods (is_production(), is_development())
   - Singleton pattern via `get_settings()`

2. **Environment Variables**:

   ```
   TELEGRAM_BOT_TOKEN=...
   DEBUG=true
   LOG_LEVEL=INFO
   LOG_FILE=logs/bot.log
   SESSION_TIMEOUT_HOURS=24
   ENVIRONMENT=development
   ```

3. **Usage**:

   ```python
   from config.settings import get_settings

   settings = get_settings()
   if settings.debug:
       logger.debug("Debug mode enabled")
   ```

### Benefits

- Centralized configuration
- Type safety
- Validation on startup
- Easy to add new settings
- No hardcoded values

---

## 5. Logging Framework

### Structure

```
utils/
└── logging_config.py    # Logging setup and configuration
```

### Flow

1. **setup_logging()**:

   - Configures root logger
   - Console handler (colored output)
   - Optional file handler
   - Reduces noise from external libraries

2. **Usage**:

   ```python
   from utils.logging_config import setup_logging
   import logging

   setup_logging(log_level='INFO', log_file='logs/bot.log')
   logger = logging.getLogger(__name__)

   logger.info("Bot started")
   logger.error("Error occurred", exc_info=True)
   ```

3. **Log Levels**:
   - DEBUG: Detailed diagnostic info
   - INFO: General informational messages
   - WARNING: Warning messages
   - ERROR: Error messages with stack traces

### Benefits

- Structured logging instead of print()
- Easy debugging with log levels
- File logging for production
- Consistent format across project
- Per-module loggers

---

## 6. Response Builder Pattern

### Structure

```
utils/
└── response_builder.py  # ResponseBuilder class
```

### Flow

1. **ResponseBuilder static methods**:

   - `success(msg)` → "✅ message"
   - `error(msg)` → "❌ message"
   - `info(msg)` → "ℹ️ message"
   - `warning(msg)` → "⚠️ message"
   - `custom(msg, emoji)` → Custom format
   - `menu(title, keyboard)` → Menu response

2. **Returns dictionary**:

   ```python
   {
       'text': "✅ Operation successful",
       'keyboard': InlineKeyboardMarkup(...),
       'parse_mode': 'HTML'
   }
   ```

3. **Usage**:

   ```python
   from utils.response_builder import ResponseBuilder

   response = ResponseBuilder.success("Report generated!")
   await client.send_message(
       msg=response['text'],
       reply_markup=response['keyboard']
   )
   ```

### Benefits

- Consistent UI/UX with emoji prefixes
- Easy to change formatting globally
- Prepared for internationalization (i18n)
- Clean separation of logic and presentation

---

## 7. Command Registry

### Structure

```
utils/
└── command_registry.py  # command_handler decorator and CommandRegistry
```

### Flow

1. **@command_handler decorator**:

   ```python
   @command_handler("start", description="Start the bot")
   async def cmd_start(self, update, context):
       ...
   ```

   - Attaches metadata to function
   - Can specify aliases

2. **CommandRegistry class**:

   - Stores all registered commands
   - `auto_register_from_instance()` - scans decorated methods
   - `generate_help_text()` - creates help message
   - `get_handler(command)` - retrieves handler

3. **Auto-registration in MainClient**:
   ```python
   def _register_commands(self):
       self.command_registry.auto_register_from_instance(self)
       for cmd, info in self.command_registry.get_all_commands().items():
           self.client.add_command_handler(cmd, info['handler'])
   ```

### Benefits

- Automatic command registration
- Self-documenting with descriptions
- Auto-generated /help command
- Support for command aliases
- Similar pattern to callback handlers

---

## Complete Request Flow

### 1. Bot Startup

```
main.py
  ↓
get_settings() - Load configuration
  ↓
setup_logging() - Configure logging
  ↓
MainClient.__init__()
  ├→ TelegramClient (singleton)
  ├→ MenuHandlers (auto-register callbacks)
  ├→ CommandRegistry (auto-register commands)
  └→ Register telegram handlers
  ↓
run_polling() - Start bot
```

### 2. User Sends /start Command

```
Telegram → on_callback → cmd_start()
  ↓
session_manager.get_session(user_id) - Get/create session
  ↓
session.set_menu("MAIN_MENU") - Track menu
  ↓
MAIN_MENU.get_buttons() - Get menu (labels used as callback_data)
  ↓
TelegramClient.inline_kb() - Create keyboard
  ↓
ResponseBuilder.menu() - Format response
  ↓
send_message() - Send to user
```

### 3. User Clicks Button

```
User clicks "Monitoring And Status" button
  ↓
Telegram sends callback_query with data="Monitoring And Status"
  ↓
on_callback() receives query
  ↓
session_manager.get_session() - Get session
  ↓
session.update_activity() - Track activity
  ↓
app_context.get_callback_handler("Monitoring And Status") - Get handler
  ↓
MenuHandlers.handle_monitor_status() - Execute handler
  ↓
ResponseBuilder.info() - Format response
  ↓
send_message() - Send to user
```

### 3a. Callback Data Generation & Matching Flow

```
STEP 1 - MENU DEFINITION (config/menus.py):
  .add_row(["Monitoring And Status", "Training Control"])
  ↓
  Menu.add_row() → uses each label directly as callback_data
  ↓
  "Monitoring And Status" → "Monitoring And Status"
  "Training Control" → "Training Control"

STEP 2 - HANDLER REGISTRATION (handlers/menu_handlers.py):
  @callback_handler("Monitoring And Status")
  async def handle_monitor_status(...):
  ↓
  Decorator → find_callback_data_from_menu()
  ↓
  Searches MAIN_MENU for "Monitoring And Status" label
  ↓
  Finds button: ("Monitoring And Status", "Monitoring And Status")
  ↓
  Returns callback_data: "Monitoring And Status"
  ↓
  Attaches: handle_monitor_status._callback_data = "Monitoring And Status"

STEP 3 - AUTO-REGISTRATION (MenuHandlers.__init__):
  self._register_callbacks()
  ↓
  Scans all methods for _callback_data attribute
  ↓
  Finds: handle_monitor_status._callback_data = "Monitoring And Status"
  ↓
  Registers: app_context["Monitoring And Status"] = handle_monitor_status

STEP 4 - USER INTERACTION:
  User clicks button → Telegram sends data="Monitoring And Status"
  ↓
  app_context.get_callback_handler("Monitoring And Status")
  ↓
  Returns: handle_monitor_status
  ↓
  Execute: await handle_monitor_status(update, context)
```

### 4. Error Occurs

```
Exception raised
  ↓
on_error() handler
  ↓
logger.error() - Log with stack trace
  ↓
ResponseBuilder.error() - Format error message
  ↓
send_message() - Inform user
```

---

## Key Improvements Summary

1. **Modular Architecture**: Handlers separated into modules
2. **Type Safety**: Menu and Settings classes with validation
3. **State Management**: Per-user sessions with tracking
4. **Configuration**: Centralized settings from environment
5. **Logging**: Structured logging instead of prints
6. **Consistent Responses**: ResponseBuilder for uniform UX
7. **Auto-Registration**: Decorators for commands and callbacks

---

## Migration Guide

### Old Code:

```python
# In main.py
@callback_handler("reports")
async def handle_reports(self, update, context):
    await self.client.send_message(msg="You pressed reports")
```

### New Code:

```python
# In handlers/menu_handlers.py
@callback_handler("Reporting And Visualization")
async def handle_reports(self, update, context):
    logger.info(f"User {update.effective_user.id} requested reports")
    response = ResponseBuilder.info("You pressed: Reporting And Visualization")
    await self.client.send_message(msg=response['text'])
```

### Benefits of Migration:

- Better organization
- Proper logging
- Consistent formatting
- Type hints
- Error handling
