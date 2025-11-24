"""Structured settings management with validation"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging
from constants.settings_constants import SettingsConstants,LogConfigConstants
# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class Settings:
    """Application settings with validation"""
    
    def __init__(self):
        """Initialize settings from environment variables"""
        # Telegram Configuration
        self.telegram_bot_token: str = self._get_required_env(SettingsConstants.TELEGRAM_BOT_TOKEN)
        
        # Debug and Logging
        self.debug: bool = os.getenv(SettingsConstants.DEBUG_VAR,
                                     SettingsConstants.DEBUG_DEFAULT).lower() in ('true', '1', 'yes')
        self.log_level: str = os.getenv(SettingsConstants.LOG_LVL_VAR,
                                         SettingsConstants.LOG_LVL).upper()
        self.log_file: Optional[str] = os.getenv(SettingsConstants.LOG_FILE_VAR)
        
        
        
        # Application Settings
        self.app_name: str = os.getenv(SettingsConstants.APP_NAME_VAR, )
        self.environment: str = os.getenv(SettingsConstants.ENVIRONMENT_VAR,SettingsConstants.ENV_TYPE.DEV )
        
        self._validate_settings()
        logger.info(f"Settings loaded for environment: {self.environment}")
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error
        
        Args:
            key: Environment variable name
            
        Returns:
            The environment variable value
            
        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
    
    def _validate_settings(self) -> None:
        """Validate settings"""
        if self.log_level not in LogConfigConstants.get_all_from_type('Log levels') :
            logger.warning(f"Invalid log level '{self.log_level}', defaulting to INFO")
            self.log_level = SettingsConstants.LOG_LVLS.INFO
        

    
    def is_production(self) -> bool:
        """Check if running in production
        
        Returns:
            True if environment is production
        """
        return self.environment.lower() == SettingsConstants.ENV_TYPE.PROD
    
    def is_development(self) -> bool:
        """Check if running in development
        
        Returns:
            True if environment is development
        """
        return self.environment.lower() == SettingsConstants.ENV_TYPE.DEV
    
    def __repr__(self) -> str:
        return f"Settings(environment={self.environment}, debug={self.debug}, log_level={self.log_level})"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
