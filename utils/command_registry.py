from constants.command_registry_fields import CommandRegistryFields
import logging
import inspect

logger = logging.getLogger(__name__)


class CommandRegistry:
    
    commands = {}

    @classmethod
    def register(cls, command: str, description: str = None):
        """Register a command handler
        
        Args:
            command: Command name
            description: Optional description for help text
            
        """
        def decorator(func):
            cls.commands[command] = {
                CommandRegistryFields.DESC: description or f"Handle /{command} command",
                CommandRegistryFields.CALLBACK: func
            }
            logger.debug(f"Registered command: /{command}")
            return func
        return decorator
    

    @classmethod
    def resolve(cls, command: str):
        """Get command info by name
        
        Args:
            command: Command name (without /)
            
        Returns:
            Command info dict or None
        """
        return cls.commands.get(command) if command in cls.commands else None   
    
    @classmethod
    async def dispatch(cls, command: str, update, context, **dependencies):
        """Dispatch a command with dependency injection
        
        Automatically finds and executes the correct command handler.
        Injects dependencies into handlers.
        
        Args:
            command: Command name (without /)
            update: Telegram update
            context: Telegram context
            
        Returns:
            Tuple of (found: bool, result)
        """
        cmd_info = cls.resolve(command)
        
        if not cmd_info:
            return False, None
        
        handler = cmd_info[CommandRegistryFields.CALLBACK]
        
        if inspect.iscoroutinefunction(handler):
            result = await handler(update, context, **dependencies)
        else:
            result = handler(update, context, **dependencies)
        
        return True, result
    
    @classmethod
    def generate_help_text(cls) -> str:
        """Generate help text from registered commands
        
        Returns:
            Formatted help text
        """
        if not cls.commands:
            return CommandRegistryFields.NO_COMMANDS_AVAILABLE_MSG
        
        help_lines = [CommandRegistryFields.AVAILABLE_COMMAND_MSG]
        for cmd, info in sorted(cls.commands.items()):
            help_lines.append(f"/{cmd} - {info[CommandRegistryFields.DESC]}")
        
        return "\n".join(help_lines)
    
    @classmethod
    def get_all_commands(cls):
        """Get all registered commands
        
        Returns:
            Dictionary of command -> info
        """
        return cls.commands.copy()
        

        