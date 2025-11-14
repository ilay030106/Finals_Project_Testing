"""Structured settings management with validation"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class Settings:
    """Application settings with validation"""
    
    def __init__(self):
        """Initialize settings from environment variables"""
        # Telegram Configuration
        self.telegram_bot_token: str = self._get_required_env('TELEGRAM_BOT_TOKEN')
        
        # Debug and Logging
        self.debug: bool = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_file: Optional[str] = os.getenv('LOG_FILE')
        
        # Session Management
        self.session_timeout_hours: int = int(os.getenv('SESSION_TIMEOUT_HOURS', '24'))
        
        # Application Settings
        self.app_name: str = os.getenv('APP_NAME', 'Telegram Bot')
        self.environment: str = os.getenv('ENVIRONMENT', 'development')
        
        self._validate()
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
    
    def _validate(self) -> None:
        """Validate settings"""
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            logger.warning(f"Invalid log level '{self.log_level}', defaulting to INFO")
            self.log_level = 'INFO'
        
        if self.session_timeout_hours < 1:
            logger.warning(f"Invalid session timeout {self.session_timeout_hours}, defaulting to 24")
            self.session_timeout_hours = 24
    
    def is_production(self) -> bool:
        """Check if running in production
        
        Returns:
            True if environment is production
        """
        return self.environment.lower() == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development
        
        Returns:
            True if environment is development
        """
        return self.environment.lower() == 'development'
    
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
