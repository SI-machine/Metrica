#!/usr/bin/env python3
"""
Command handlers for bot commands using python-telegram-bot
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import KeyboardTemplates
import logging
from auth.decorators import require_auth

logger = logging.getLogger(__name__)

@require_auth
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_name = update.effective_user.first_name
    text = f"Welcome to Metrica Bot, {user_name}!\n\nI'm here to help you. Use /help for more info."
    
    await update.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.main_menu()
    )
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    text = """
<b>Available Commands:</b>

/start - Start the bot
/help - Show this help
/about - About the bot

<b>Features:</b>
• Interactive buttons
• Message handling
• Simple and reliable

Just send me a message!
    """
    await update.message.reply_text(text, parse_mode='HTML')
    logger.info(f"User {update.effective_user.id} requested help")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command"""
    text = """
<b>Metrica Bot</b>

A simple Telegram bot built with Python and python-telegram-bot framework.

<b>Version:</b> 2.0.0
<b>Language:</b> Python 3
<b>Framework:</b> python-telegram-bot

Built for the Metrica project.
    """
    await update.message.reply_text(text, parse_mode='HTML')
    logger.info(f"User {update.effective_user.id} requested about info")

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /get_my_id command"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    await update.message.reply_text(
        f"<b>Your Telegram Info:</b>\n\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n"
        f"First Name: {first_name}\n\n",
        parse_mode='HTML'
    )