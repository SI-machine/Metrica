#!/usr/bin/env python3
"""
Metrica Bot - A modular Telegram bot using python-telegram-bot framework
"""

import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    filters, ConversationHandler
)

from config import Config, ALLOWED_USERS
from utils.logging_config import setup_logging
from handlers.command_handler import start_command, help_command, about_command, get_my_id
from handlers.callback_handler import button_callback
from handlers.message_handler import handle_text_message
from handlers.media_handler import (
    handle_photo, handle_document, handle_video, 
    handle_audio, handle_voice, handle_sticker
)
from handlers.order_form_handler import (
    start_order_form, receive_client_name, receive_description,
    receive_employee_name, receive_income_value, receive_client_contact,
    skip_description, skip_contact, confirm_order, cancel_order_form,
    cancel_order_form_message, select_employee,
    WAITING_CLIENT_NAME, WAITING_DESCRIPTION, WAITING_EMPLOYEE_NAME,
    WAITING_INCOME_VALUE, WAITING_CLIENT_CONTACT, CONFIRMING_ORDER
)
from handlers.employee_form_handler import (
    start_employee_form, receive_employee_name as receive_emp_name_form,
    receive_phone_number, skip_phone, receive_payment_method,
    receive_payment_value, receive_date_started, receive_email,
    skip_email, receive_notes, skip_notes, confirm_employee,
    cancel_employee_form, cancel_employee_form_message,
    WAITING_EMPLOYEE_NAME as WAITING_EMP_NAME, WAITING_PHONE_NUMBER,
    WAITING_PAYMENT_METHOD, WAITING_PAYMENT_VALUE, WAITING_DATE_STARTED,
    WAITING_EMAIL, WAITING_NOTES, CONFIRMING_EMPLOYEE
)
from database.models import init_db

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
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        print(f"Warning: Database initialization failed: {e}")
    
    # Create application
    application = Application.builder().token(config.bot_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("get_my_id", get_my_id))
    
    # Register order form ConversationHandler (must be before CallbackQueryHandler)
    order_form_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_order_form, pattern='^add_order_'),
            CallbackQueryHandler(start_order_form, pattern='^order_add_today$')
        ],
        states={
            WAITING_CLIENT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_client_name),
                CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
            ],
            WAITING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description),
                CallbackQueryHandler(skip_description, pattern='^skip_description$'),
                CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
            ],
            WAITING_EMPLOYEE_NAME: [
                CallbackQueryHandler(select_employee, pattern='^select_employee_'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_employee_name),
                CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
            ],
            WAITING_INCOME_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_income_value),
                CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
            ],
            WAITING_CLIENT_CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_client_contact),
                CallbackQueryHandler(skip_contact, pattern='^skip_contact$'),
                CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
            ],
            CONFIRMING_ORDER: [
                CallbackQueryHandler(confirm_order, pattern='^confirm_order$'),
                CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_order_form_message),
            CallbackQueryHandler(cancel_order_form, pattern='^cancel_order_form$')
        ],
        name="order_form"
    )
    application.add_handler(order_form_handler)
    
    # Register employee form ConversationHandler
    employee_form_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_employee_form, pattern='^add_employee$')
        ],
        states={
            WAITING_EMP_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_emp_name_form),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            WAITING_PHONE_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone_number),
                CallbackQueryHandler(skip_phone, pattern='^skip_phone$'),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            WAITING_PAYMENT_METHOD: [
                CallbackQueryHandler(receive_payment_method, pattern='^payment_(owner|in_percent|fixed)$'),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            WAITING_PAYMENT_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_payment_value),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            WAITING_DATE_STARTED: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date_started),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            WAITING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email),
                CallbackQueryHandler(skip_email, pattern='^skip_email$'),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            WAITING_NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_notes),
                CallbackQueryHandler(skip_notes, pattern='^skip_notes$'),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ],
            CONFIRMING_EMPLOYEE: [
                CallbackQueryHandler(confirm_employee, pattern='^confirm_employee$'),
                CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_employee_form_message),
            CallbackQueryHandler(cancel_employee_form, pattern='^cancel_employee_form$')
        ],
        name="employee_form"
    )
    application.add_handler(employee_form_handler)
    
    # Register callback handler for button clicks (after ConversationHandler)
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