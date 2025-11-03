#!/usr/bin/env python3
"""
Message handler for processing regular text messages using python-telegram-bot
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging
from auth.decorators import require_auth

logger = logging.getLogger(__name__)

@require_auth
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages"""
    text = update.message.text
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    
    logger.info(f"User {user_id} sent message: {text}")
    
    try:
        response = _process_message(text, user_name)
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text("Sorry, something went wrong. Please try again.")

def _process_message(text: str, user_name: str) -> str:
    """Process the message text and generate response"""
    text_lower = text.lower()
    
    if text_lower in ['hello', 'hi', 'hey']:
        return f"Hello {user_name}! How can I help you?"
    elif text_lower in ['bye', 'goodbye']:
        return f"Goodbye {user_name}!"
    elif text_lower in ['thanks', 'thank you']:
        return f"You're welcome, {user_name}!"
    elif text_lower in ['how are you', 'how are you?']:
        return "I'm doing great! Thanks for asking. How can I help you today?"
    else:
        return f"You said: '{text}'\n\nI received your message!"