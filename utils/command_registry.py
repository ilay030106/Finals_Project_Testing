"""Command registry decorator for automatic command registration"""
from typing import Callable, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def command_handler(
    command: str,
    description: Optional[str] = None,
    aliases: Optional[list] = None
):
    """Decorator to register command handlers automatically
    
    Args:
        command: The command name (without /)
        description: Optional description for help text
        aliases: Optional list of command aliases
    
    Usage:
        @command_handler("start", description="Start the bot")
        async def cmd_start(self, update, context):
            ...
    """
    def decorator(func: Callable):
        # Attach command metadata to the function
        func._command = command
        func._command_description = description or f"Handle /{command} command"
        func._command_aliases = aliases or []
        
        logger.debug(f"Registered command: /{command}")
        return func
    return decorator


class CommandRegistry:
    """Registry for managing command handlers"""
    
    def __init__(self):
        """Initialize command registry"""
        self.commands: Dict[str, dict] = {}
        self.logger = logger
    
    def register(self, command: str, handler: Callable, description: Optional[str] = None) -> None:
        """Register a command handler
        
        Args:
            command: Command name
            handler: Handler function
            description: Optional description
        """
        self.commands[command] = {
            'handler': handler,
            'description': description or f"Handle /{command} command"
        }
        self.logger.info(f"Registered command: /{command}")
    
    def get_handler(self, command: str) -> Optional[Callable]:
        """Get handler for a command
        
        Args:
            command: Command name
            
        Returns:
            Handler function or None
        """
        cmd_info = self.commands.get(command)
        return cmd_info['handler'] if cmd_info else None
    
    def get_all_commands(self) -> Dict[str, dict]:
        """Get all registered commands
        
        Returns:
            Dictionary of command -> info
        """
        return self.commands.copy()
    
    def generate_help_text(self) -> str:
        """Generate help text from registered commands
        
        Returns:
            Formatted help text
        """
        if not self.commands:
            return "No commands available."
        
        help_lines = ["📋 Available Commands:\n"]
        for cmd, info in sorted(self.commands.items()):
            help_lines.append(f"/{cmd} - {info['description']}")
        
        return "\n".join(help_lines)
    
    def auto_register_from_instance(self, instance: object) -> int:
        """Auto-register all decorated command methods from an instance
        
        Args:
            instance: Object instance to scan for decorated methods
            
        Returns:
            Number of commands registered
        """
        count = 0
        for attr_name in dir(instance):
            attr = getattr(instance, attr_name)
            if callable(attr) and hasattr(attr, '_command'):
                self.register(
                    attr._command,
                    attr,
                    attr._command_description
                )
                
                # Register aliases
                for alias in getattr(attr, '_command_aliases', []):
                    self.register(alias, attr, f"Alias for /{attr._command}")
                
                count += 1
        
        self.logger.info(f"Auto-registered {count} commands from {instance.__class__.__name__}")
        return count
