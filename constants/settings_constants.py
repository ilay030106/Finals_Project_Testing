from enum import StrEnum

class SettingsConstants(StrEnum):
    TELEGRAM_BOT_TOKEN='TELEGRAM_BOT_TOKEN'
    DEBUG_VAR = 'DEBUG'
    DEBUG_DEFAULT = 'False'
    LOG_LVL_VAR =  'False'
    LOG_LVL = 'INFO'
    LOG_FILE_VAR = 'LOG_FILE'
    APP_NAME_VAR = 'APP_NAME'
    APP_NAME_DEFAULT = 'Telegram Bot'
    ENVIRONMENT_VAR = 'ENVIRONMENT'
    class ENV_TYPE(StrEnum):
        PROD = 'production'
        DEV = 'development'

class LogConfigConstants(StrEnum):
    LOGGER_TELEGRAM = 'telegram'
    LOGGER_HTTPX = 'httpx'
    LOGGER_HTTPCORE = 'httpcore'
    LVL_DEBUG = 'DEBUG'
    LVL_INFO= 'INFO'
    LVL_WARNING = 'WARNING'
    LVL_ERROR = 'ERROR'
    LVL_CRITICAL = 'CRITICAL'

    @classmethod
    def get_all_from_type(cls,type:str):
        if type.lower() in ['logger','loggers']:
            return [e for e in cls if e.name.startswith('LOGGER_')]
        
        elif type.lower() in ['log levels','log lvls','lvls','levels','log_levels','log_lvls']:
            return [e for e in cls if e.name.startswith('LVL_')]