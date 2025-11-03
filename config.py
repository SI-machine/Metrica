#!/usr/bin/env python3
"""
Configuration management for Metrica Bot
"""

import os
from typing import Optional
from typing import List

class Config:
    """Bot configuration management"""
    
    def __init__(self):
        self.bot_token: Optional[str] = None
        self.webhook_url: Optional[str] = None
        self.webhook_port: int = 8443
        self.debug: bool = False
        self.log_level: str = "INFO"
        
        self._load_from_env()

        # Load allowed users from environment
        self.allowed_users: List[int] = self._load_allowed_users()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        self.bot_token = os.getenv('BOT_TOKEN')
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.webhook_port = int(os.getenv('WEBHOOK_PORT', '8443'))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Try to load from .env file if not found in environment
        if not self.bot_token:
            self._load_from_env_file()
    
    def _load_from_env_file(self):
        """Load from .env file manually"""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key == 'BOT_TOKEN':
                            self.bot_token = value.strip()
                        elif key == 'WEBHOOK_URL':
                            self.webhook_url = value.strip()
                        elif key == 'WEBHOOK_PORT':
                            self.webhook_port = int(value.strip())
                        elif key == 'DEBUG':
                            self.debug = value.strip().lower() == 'true'
                        elif key == 'LOG_LEVEL':
                            self.log_level = value.strip()
        except FileNotFoundError:
            pass
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.bot_token:
            return False
        return True
    
    def get_error_message(self) -> str:
        """Get error message for invalid configuration"""
        if not self.bot_token:
            return (
                "Error: BOT_TOKEN not found!\n"
                "Please:\n"
                "1. Create a .env file\n"
                "2. Add: BOT_TOKEN=your_token_here\n"
                "3. Get token from @BotFather"
            )
        return "Configuration error"

    def _load_allowed_users(self) -> List[int]:
        """Load list of allowed user IDs from environment"""

        allowed_users_str = os.getenv('ALLOWED_USERS', '')
        
        # Try to load from .env file if not found in environment
        if not allowed_users_str:
            allowed_users_str = self._load_allowed_users_from_env_file()
        
        if not allowed_users_str:
            return []
        
        try:
            # Parse comma-separated user IDs
            user_ids = [int(uid.strip()) for uid in allowed_users_str.split(',') if uid.strip()]
            return user_ids
        except ValueError:
            print("Warning: Invalid ALLOWED_USERS format. Should be comma-separated integers.")
            return []
    
    def _load_allowed_users_from_env_file(self) -> str:
        """Load ALLOWED_USERS from .env file manually"""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key == 'ALLOWED_USERS':
                            return value.strip()
        except FileNotFoundError:
            pass
        return ''
    
    # Add this method to your Config class
    def get_allowed_users(self) -> List[int]:
        """Get list of allowed user IDs"""
        return self.allowed_users

ALLOWED_USERS = []