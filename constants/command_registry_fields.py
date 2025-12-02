from enum import StrEnum

class CommandRegistryFields(StrEnum):
    DESC = "desc"
    CALLBACK="callback"
    NO_COMMANDS_AVAILABLE_MSG="No commands available."
    AVAILABLE_COMMAND_MSG="📋 Available Commands:\n"