#!/usr/bin/env python3
"""
Authentication decorators for access control
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging
from config import Config

logger = logging.getLogger(__name__)

def require_auth(func):
    """Decorator to restrict access to authorize users only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):

        config = Config()
        ALLOWED_USERS = config.get_allowed_users()
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"

        if user_id not in ALLOWED_USERS:
            logger.warning(f"Unauthorized access attempt by user {user_id} (@{username})")

            # Send friendly message
            await update.message.reply_text(
                "🔒 <b>Access Restricted</b>\n\n"
                "This feature is only available to authorized users.\n"
                "Contact an administrator if you believe this is an error.\n\n"
                "You can still use /help to see available commands.",
                parse_mode='HTML'
            )
            return

        logger.info(f"Authorized access by user {user_id} (@{username})")
        return await func(update, context)
    
    return wrapper

def require_auth_callback(func):
    """Decorator for callback queries (button clicks)"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        config = Config()
        ALLOWED_USERS = config.get_allowed_users() 
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        if user_id not in ALLOWED_USERS:
            logger.warning(f"Unauthorized callback attempt by user {user_id} (@{username})")
            
            # Answer callback query first
            await update.callback_query.answer()
            
            # Send message to user
            await update.callback_query.message.reply_text(
                "🔒 <b>Access Restricted</b>\n\n"
                "This feature is only available to authorized users.\n"
                "Contact an administrator if you believe this is an error.",
                parse_mode='HTML'
            )
            return
        
        logger.info(f"Authorized callback access by user {user_id} (@{username})")
        return await func(update, context)
    
    return wrapper

