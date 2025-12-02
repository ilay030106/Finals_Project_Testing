from constants.command_registry_fields import CommandRegistryFields
import logging

logger = logging.getLogger(__name__)


class CommandRegistry:
    
    commands = {}

    @classmethod
    def register(cls,command:str,desc:str=None):
        def decorator(func):
            cls.commands[command] = {
                CommandRegistryFields.DESC : desc,
                CommandRegistryFields.CALLBACK : func
            }
            return func
        return decorator
    

    @classmethod
    def resolve(cls,command:str):
        return cls.commands.get(command) if command in cls.commands else None   
    
    @classmethod
    def generate_help_text(self) -> str:
        """Generate help text from registered commands
        
        Returns:
            Formatted help text
        """
        if not self.commands:
            return CommandRegistryFields.NO_COMMANDS_AVAILABLE_MSG
        
        help_lines = [CommandRegistryFields.AVAILABLE_COMMAND_MSG]
        for cmd, info in sorted(self.commands.items()):
            help_lines.append(f"/{cmd} - {info[CommandRegistryFields.DESC]}")    
    
    @classmethod
    def get_all_commands(self):
        """Get all registered commands
        
        Returns:
            Dictionary of command -> info
        """
        return self.commands.copy()
        

        