#!/usr/bin/env python3
"""
Metrica Bot - A modular Telegram bot using python-telegram-bot framework
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import Config, ALLOWED_USERS
from utils.logging_config import setup_logging
from handlers.command_handler import start_command, help_command, about_command, get_my_id
from handlers.callback_handler import button_callback
from handlers.message_handler import handle_text_message
from handlers.media_handler import (
    handle_photo, handle_document, handle_video, 
    handle_audio, handle_voice, handle_sticker
)

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context) -> None:
    """Handle errors that occur during update processing"""
    logger.error(f"Update {update} caused error: {context.error}")
    
    # Try to send error message to user if possible
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Sorry, something went wrong while processing your request. Please try again."
            )
        except Exception as e:
            logger.error(f"Could not send error message to user: {e}")

def main():
    """Start the bot"""
    # Load configuration
    config = Config()
    
    if not config.validate():
        print(config.get_error_message())
        return

    # Initialize allowed users
    global ALLOWED_USERS
    ALLOWED_USERS = config.get_allowed_users()

    if not ALLOWED_USERS:
        print("No allowed users found. Please set ALLOWED_USERS in environment variables.")
    
    # Setup logging
    setup_logging(config.log_level, config.debug)
    
    logger.info("Starting Metrica Bot with python-telegram-bot framework...")
    
    # Create application
    application = Application.builder().token(config.bot_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("get_my_id", get_my_id))
    
    # Register callback handler for button clicks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Register text message handler (excluding commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Register media handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot (polling mode)
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()