# Project Architecture Documentation

## Overview

This Telegram bot project uses a **dependency injection** architecture with **explicit handler registration** through decorators. The design prioritizes clarity, testability, and scalability for future ML integration.

---

## Core Principles

1. **Dependency Injection**: Dependencies are passed explicitly to handlers, not accessed globally
2. **Standalone Functions**: Handlers are pure functions, not instance methods
3. **Decorator-based Registration**: Handlers auto-register using `@CallbackRegistry.register()`
4. **Type Safety**: Clear function signatures with type hints
5. **Separation of Concerns**: Menus define structure, handlers implement logic

---

## Project Structure

```
Finals_Project_Testing/
├── main.py                      # Application entry point
├── TelegramClient.py            # Telegram API wrapper (singleton)
├── app_context.py               # Global context for user state
├── config/
│   ├── settings.py             # Environment-based configuration
│   └── __init__.py
├── constants/
│   ├── main_client_constants.py
│   ├── main_menu_constants.py
│   ├── telegram_client_constants.py
│   ├── response_fields.py
│   ├── app_context_fields.py
│   └── __init__.py
├── menus/
│   ├── base_menu.py            # Base class for menu structure
│   ├── menu.py                 # Menu builder classes
│   ├── main_menu.py            # Main menu + handlers
│   └── __init__.py
├── utils/
│   ├── callback_registry.py    # Callback handler registry
│   ├── command_registry.py     # Command handler registry
│   ├── response_builder.py     # Consistent response formatting
│   ├── logging_config.py       # Logging configuration
│   └── telegram_client_utils.py
└──
```

---

## 1. Dependency Injection System

### Architecture

The bot uses **explicit dependency injection** where handlers receive all dependencies as function parameters:

```python
# Handler signature with explicit dependencies
@CallbackRegistry.register("Settings")
async def handle_settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    client,      # ← Injected dependency
    **kwargs     # ← Additional dependencies (model, trainer, etc.)
) -> None:
    await client.send_message(msg="Settings")
```

### Flow

1. **MainClient creates dependencies**:

```python
class MainClient:
    def __init__(self):
        self.client = TelegramClient()
        self.main_menu = MainMenu(self.client)
        # Future: self.model, self.trainer, self.monitor
```

2. **Dependencies passed to dispatcher**:

```python
async def on_callback(self, update, context):
    found, result = await CallbackRegistry.dispatch(
        update,
        context,
        client=self.client,           # ← Pass dependencies
        main_menu=self.main_menu,
        # Future additions:
        # model=self.model,
        # trainer=self.trainer,
        # monitor=self.monitor
    )
```

3. **Registry injects dependencies into handlers**:

```python
class CallbackRegistry:
    @classmethod
    async def dispatch(cls, update, context, **dependencies):
        handler, params = cls.resolve(callback_data)
        # Inject all dependencies
        result = await handler(update, context, *params, **dependencies)
```

### Benefits

- ✅ **Clear dependencies**: Each handler declares what it needs
- ✅ **Easy testing**: Mock dependencies without globals
- ✅ **Type-safe**: Can add type hints for better IDE support
- ✅ **Scalable**: Easy to add new dependencies (ML models, services)
- ✅ **No hidden coupling**: No global state access

---

## 2. Callback Registry System

### Structure

```python
class CallbackRegistry:
    static_handlers = {}      # Maps callback_data → handler function
    pattern_handlers = []     # List of (regex, handler) for dynamic routing
```

### Registration

**Decorator-based registration** at module level:

```python
@CallbackRegistry.register(MainMenuFields.SETTINGS)
async def handle_settings(update, context, client, **kwargs):
    """Handler is registered when module is imported"""
    ...
```

### Resolution & Dispatch

```python
@classmethod
async def dispatch(cls, update, context, **dependencies):
    """
    1. Extract callback_data from update
    2. Find handler using resolve()
    3. Inject dependencies and execute handler
    """
    callback_data = update.callback_query.data
    handler, params = cls.resolve(callback_data)

    if handler:
        result = await handler(update, context, *params, **dependencies)
        return True, result
    return False, None
```

### Pattern Matching (Advanced)

For dynamic callbacks:

```python
@CallbackRegistry.register_pattern(r"page_(\d+)")
async def handle_pagination(update, context, client, page_num, **kwargs):
    """Extracts page number from callback_data like 'page_3'"""
    await client.send_message(msg=f"Showing page {page_num}")
```

---

## 3. Menu System

### Architecture

Menus use a **builder pattern** with **separation of structure and logic**:

- **BaseMenu**: Provides menu creation and display
- **Menu class**: Builder for menu structure
- **Standalone handlers**: Implement button logic separately

### Menu Definition

```python
class MainMenu(BaseMenu):
    def __init__(self, client):
        super().__init__(
            client,
            MainMenuFields.TITLE,  # "Welcome To The Control Center!"
            [
                [MainMenuFields.MONITOR_AND_STATUS, MainMenuFields.TRAINING_CONTROL],
                [MainMenuFields.REPORT_AND_VISUAL, MainMenuFields.SETTINGS]
            ]
        )
```

This creates:

- Row 1: ["Monitoring And Status", "Training Control"]
- Row 2: ["Reporting And Visualization", "Settings"]

### Button Labels = Callback Data

By default, button **labels are used as callback_data**:

- Button label: "Settings"
- Callback data sent: "Settings"
- Handler registered: `@CallbackRegistry.register("Settings")`

### Handler Implementation

Handlers are **standalone functions** defined at module level:

```python
# In menus/main_menu.py

@CallbackRegistry.register(MainMenuFields.SETTINGS)
async def handle_settings(update, context, client, **kwargs):
    """Standalone function - not a method!"""
    response = ResponseBuilder.info("Settings menu")
    await client.send_message(msg=response[ResponseFields.TEXT])
```

### Display Flow

```python
# In cmd_start:
await self.main_menu.show_menu(chat_id=user_id)
  ↓
# BaseMenu.show_menu():
reply_markup = TelegramClient.inline_kb(self.menu.get_buttons())
response = ResponseBuilder.menu(title, keyboard)
await client.send_message(...)
```

---

## 4. Command Registry System

### Structure

Similar to CallbackRegistry but for `/commands`:

```python
@command_handler("start", description="Start the bot")
async def cmd_start(self, update, context):
    """Command handlers are instance methods"""
    ...
```

### Auto-registration

```python
def _register_commands(self):
    # Scan MainClient for @command_handler decorated methods
    self.command_registry.auto_register_from_instance(self)

    # Register with Telegram client
    for cmd, info in self.command_registry.get_all_commands().items():
        self.client.add_command_handler(cmd, info['handler'])
```

### Auto-generated Help

```python
def generate_help_text(self):
    """📋 Available Commands:

    /start - Start the bot
    /help - Show available commands
    """
```

---

## 5. Response Builder Pattern

### Consistent Message Formatting

```python
class ResponseBuilder:
    @staticmethod
    def success(msg) -> dict:
        return {'text': f"✅ {msg}", 'keyboard': None, 'parse_mode': None}

    @staticmethod
    def error(msg) -> dict:
        return {'text': f"❌ {msg}", 'keyboard': None, 'parse_mode': None}

    @staticmethod
    def info(msg) -> dict:
        return {'text': f"ℹ️ {msg}", 'keyboard': None, 'parse_mode': None}
```

### Usage

```python
response = ResponseBuilder.success("Training started!")
await client.send_message(msg=response[ResponseFields.TEXT])
```

### Benefits

- Consistent UI with emoji prefixes
- Easy to change globally
- Prepared for i18n
- Returns dictionary for flexibility

---

## 6. Configuration Management

### Settings Class

```python
from config.settings import get_settings

settings = get_settings()  # Singleton

settings.telegram_bot_token
settings.debug
settings.log_level
settings.environment  # 'development' or 'production'
```

### Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_token_here
DEBUG=true
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
ENVIRONMENT=development
```

### Validation

Settings are validated on startup:

- Required variables checked
- Type conversion (str → bool, int)
- Sensible defaults provided

---

## 7. Logging System

### Setup

```python
setup_logging(
    log_level=settings.log_level,  # INFO, DEBUG, ERROR
    log_file=settings.log_file     # Optional file output
)
```

### Usage

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Bot started")
logger.debug(f"Received callback: {callback_data}")
logger.error("Error occurred", exc_info=True)
```

### Benefits

- Structured logging instead of print()
- Per-module loggers
- Stack traces for errors
- File + console output

---

## 8. State Management

### App Context

For single-user bot, `app_context` provides simple state storage:

```python
from app_context import app_context
from constants.app_context_fields import AppContextFields

# Store
app_context[AppContextFields.USER_ID] = user_id
app_context[AppContextFields.USER_NAME] = username
app_context[AppContextFields.CLIENT] = self.client
app_context[AppContextFields.MAIN_MENU] = self.main_menu

# Retrieve
user_id = app_context[AppContextFields.USER_ID]
client = app_context.get(AppContextFields.CLIENT)
```

### Why Not Session Manager?

For a **single-user bot**:

- No need for per-user sessions
- App context is simpler
- Less overhead
- Still extensible if needed later

---

## Complete Request Flow

### Bot Startup

```
main.py execution
  ↓
get_settings() → Load environment config
  ↓
setup_logging() → Configure logging
  ↓
MainClient.__init__()
  ├→ TelegramClient() - Singleton instance
  ├→ CommandRegistry() - Create registry
  ├→ MainMenu(client) - Create menu
  ├→ app_context[CLIENT] = self.client - Store for reference
  ├→ _register_commands() - Scan & register @command_handler
  └→ Register telegram handlers (on_text, on_error, on_callback)
  ↓
run_polling() → Start bot
```

### User Clicks Button Flow

```
1. USER ACTION
   User clicks "Settings" button in Telegram
     ↓

2. TELEGRAM API
   Telegram sends CallbackQuery with data="Settings"
     ↓

3. BOT RECEIVES
   MainClient.on_callback(update, context)
     ↓

4. DISPATCH WITH DEPENDENCIES
   await CallbackRegistry.dispatch(
       update,
       context,
       client=self.client,        ← Inject dependencies
       main_menu=self.main_menu
   )
     ↓

5. RESOLVE HANDLER
   CallbackRegistry.resolve("Settings")
   → Returns: handle_settings function
     ↓

6. INJECT & EXECUTE
   await handle_settings(
       update,
       context,
       client=self.client,        ← Dependencies injected
       main_menu=self.main_menu
   )
     ↓

7. HANDLER LOGIC
   def handle_settings(update, context, client, **kwargs):
       response = ResponseBuilder.info("Settings")
       await client.send_message(msg=response['text'])
     ↓

8. RESPONSE SENT
   User receives: "ℹ️ Settings"
```

### Command Flow (/start)

```
1. USER TYPES
   /start
     ↓

2. TELEGRAM API
   Telegram sends Message with text="/start"
     ↓

3. COMMAND HANDLER
   MainClient.cmd_start(update, context)
   (Registered via @command_handler decorator)
     ↓

4. STORE USER INFO
   app_context[USER_ID] = user_id
   app_context[USER_NAME] = username
     ↓

5. SHOW MENU
   await self.main_menu.show_menu(chat_id=user_id)
     ↓

6. BUILD KEYBOARD
   reply_markup = TelegramClient.inline_kb(menu.get_buttons())
     ↓

7. SEND MESSAGE
   await client.send_message(msg=title, reply_markup=reply_markup)
     ↓

8. USER SEES
   "Welcome To The Control Center!"
   [Monitoring And Status] [Training Control]
   [Reporting And Visualization] [Settings]
```

---

## Future ML Integration

The dependency injection architecture is designed for ML systems:

### Adding ML Components

```python
class MainClient:
    def __init__(self):
        self.client = TelegramClient()
        self.main_menu = MainMenu(self.client)

        # ML Components
        self.model = YourMLModel()
        self.trainer = ModelTrainer(self.model)
        self.monitor = TrainingMonitor()
        self.data_loader = DataLoader()

async def on_callback(self, update, context):
    found, result = await CallbackRegistry.dispatch(
        update,
        context,
        client=self.client,
        model=self.model,           # ← ML model
        trainer=self.trainer,       # ← Training service
        monitor=self.monitor,       # ← Monitoring
        data_loader=self.data_loader  # ← Data handling
    )
```

### ML Handlers

```python
@CallbackRegistry.register("Start Training")
async def handle_start_training(update, context, client, trainer, model, **kwargs):
    """Handler receives only what it needs"""
    await trainer.start_training()
    response = ResponseBuilder.success("Training started!")
    await client.send_message(msg=response[ResponseFields.TEXT])

@CallbackRegistry.register("Check Status")
async def handle_check_status(update, context, client, monitor, **kwargs):
    """Different handler, different dependencies"""
    status = await monitor.get_status()
    response = ResponseBuilder.info(f"Status: {status}")
    await client.send_message(msg=response[ResponseFields.TEXT])
```

### Benefits for ML

- ✅ **Clear dependencies**: Each handler declares ML components it uses
- ✅ **Easy testing**: Mock model/trainer for tests
- ✅ **Type-safe**: Add type hints like `trainer: ModelTrainer`
- ✅ **Modular**: Add/remove ML services without changing handlers
- ✅ **Scalable**: Support multiple models, experiments, etc.

---

## Key Design Decisions

### 1. Why Standalone Functions Instead of Methods?

**Problem**: Instance methods need `self`, causing binding complexity.

**Solution**: Use standalone functions with explicit dependencies.

```python
# ❌ Complex - needs instance binding
class MainMenu(BaseMenu):
    @callback_handler("Settings")
    async def handle_settings(self, update, context):
        await self.client.send_message(...)

# ✅ Simple - just a function
@CallbackRegistry.register("Settings")
async def handle_settings(update, context, client, **kwargs):
    await client.send_message(...)
```

### 2. Why Dependency Injection Over Global State?

**Problem**: Global `app_context` creates hidden dependencies.

**Solution**: Pass dependencies explicitly.

```python
# ❌ Hidden dependency
async def handle_settings(update, context):
    client = app_context['client']  # Where does this come from?

# ✅ Explicit dependency
async def handle_settings(update, context, client, **kwargs):
    # Clear what this function needs
```

### 3. Why Class-level Decorator Registration?

**Problem**: Need simple registration syntax.

**Solution**: Decorators at module level.

```python
# ✅ Clean and declarative
@CallbackRegistry.register("Settings")
async def handle_settings(update, context, client, **kwargs):
    ...
```

Handlers register when module imports, no manual registration needed.

---

## Testing Strategy

The architecture enables easy testing:

```python
# Test handler in isolation
async def test_handle_settings():
    # Mock dependencies
    mock_client = Mock(TelegramClient)
    mock_update = Mock(Update)
    mock_context = Mock(ContextTypes.DEFAULT_TYPE)

    # Call handler directly with mocks
    await handle_settings(
        mock_update,
        mock_context,
        client=mock_client
    )

    # Verify behavior
    mock_client.send_message.assert_called_once()
```

---

## Migration Notes

### Old Architecture (Session-based, Instance Methods)

```python
# Old: Instance methods with session management
class MainMenu(BaseMenu):
    @callback_handler("Settings")
    async def handle_settings(self, update, context):
        session = session_manager.get_session(update.effective_user.id)
        await self.client.send_message(...)
```

### New Architecture (Dependency Injection, Functions)

```python
# New: Standalone functions with explicit dependencies
@CallbackRegistry.register("Settings")
async def handle_settings(update, context, client, **kwargs):
    # No session needed for single-user bot
    await client.send_message(...)
```

### Changes Made

1. ✅ Removed `SessionManager` (unnecessary for single user)
2. ✅ Converted handlers to standalone functions
3. ✅ Added dependency injection to `CallbackRegistry.dispatch()`
4. ✅ Simplified `app_context` to basic state storage
5. ✅ Prepared for ML integration with `**kwargs` pattern

---

## Summary

This architecture provides:

- **Clarity**: Explicit dependencies, no hidden globals
- **Testability**: Easy to mock and test in isolation
- **Scalability**: Ready for ML systems with multiple services
- **Simplicity**: No complex binding or registration logic
- **Type Safety**: Clear function signatures with type hints
- **Maintainability**: Easy to add new features and handlers

The design balances pragmatism (simple for current needs) with future-proofing (ready for ML integration).
