"""
Utility functions for Metrica Bot
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def format_user_info(user) -> str:
    """Format user information for display"""
    info = f"👤 **User Info:**\n"
    info += f"• Name: {user.first_name}"
    if user.last_name:
        info += f" {user.last_name}"
    info += f"\n• Username: @{user.username}" if user.username else "\n• Username: Not set"
    info += f"\n• ID: `{user.id}`"
    return info

def log_user_action(user, action: str, details: str = ""):
    """Log user actions for analytics"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] User {user.id} ({user.first_name}) - {action}"
    if details:
        log_message += f" - {details}"
    logger.info(log_message)

def create_error_message(error: Exception) -> str:
    """Create user-friendly error message"""
    return f"❌ **Oops! Something went wrong:**\n\n`{str(error)}`\n\nPlease try again or contact support if the problem persists."

def validate_message_length(text: str, max_length: int = 4096) -> bool:
    """Validate if message length is within Telegram limits"""
    return len(text) <= max_length

def truncate_message(text: str, max_length: int = 4096) -> str:
    """Truncate message if it exceeds Telegram limits"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

def create_status_message(status: str, details: Dict[str, Any] = None) -> str:
    """Create a status message with optional details"""
    message = f"📊 **Status:** {status}\n"
    if details:
        for key, value in details.items():
            message += f"• {key}: {value}\n"
    return message
