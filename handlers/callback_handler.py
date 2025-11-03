#!/usr/bin/env python3
"""
Callback handler for processing inline keyboard callbacks using python-telegram-bot
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import KeyboardTemplates
from utils.calendar_utils import create_calendar
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime
import logging
from auth.decorators import require_auth_callback

logger = logging.getLogger(__name__)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    
    # Answer the callback query first to prevent duplicate responses
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    logger.info(f"User {user_id} clicked button: {callback_data}")
    
    try:
        # Check known callbacks first
        if callback_data == 'start':
            await _handle_start(query, update.effective_user.first_name)
        elif callback_data == 'menu':
            await _handle_menu(update, context)
        elif callback_data == 'about':
            await _handle_about(query)
        elif callback_data == 'help':
            await _handle_help(query)
        elif callback_data == 'calendar':
            await _handle_calendar(update, context)
        elif callback_data == 'settings':
            await _handle_settings(update, context)
        elif callback_data == 'reports':
            await _handle_reports(update, context)
        elif callback_data == 'tools':
            await _handle_tools(update, context)
        else:
            # Try to handle as calendar navigation callback
            # Calendar callbacks have specific format that DetailedTelegramCalendar can process
            try:
                # Check if it's a calendar callback by trying to create a calendar instance
                # The process method might raise exceptions for invalid data
                test_calendar = DetailedTelegramCalendar()
                # Try processing - if it works without raising ValueError/TypeError, it's likely a calendar callback
                result, key, step = test_calendar.process(callback_data)
                # It's a calendar callback - handle it
                await _handle_calendar_navigation(update, context)
            except (ValueError, AttributeError, TypeError, Exception):
                # Not a calendar callback either - might be add_order_* or other future callbacks
                # Check for add_order pattern
                if callback_data.startswith('add_order_'):
                    # TODO: Handle add order callback
                    await query.message.reply_text("Add order feature coming soon!")
                else:
                    await query.message.reply_text("Unknown action. Please try again.")
            
    except Exception as e:
        logger.error(f"Error handling callback {callback_data}: {e}")
        await query.message.reply_text("Sorry, something went wrong. Please try again.")

async def _handle_start(query, user_name: str) -> None:
    """Handle start callback"""
    text = f"Welcome to Metrica Bot, {user_name}!\n\nI'm here to help you. Use /help for more info."
    await query.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.main_menu()
    )

@require_auth_callback
async def _handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu callback"""
    query = update.callback_query
    text = "<b>Main Menu</b>\n\nChoose an option:"
    await query.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.submenu(),
        parse_mode='HTML'
    )

async def _handle_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle about callback"""
    query = update.callback_query
    text = """
<b>Metrica Bot</b>

A simple Telegram bot built with Python and python-telegram-bot framework.

<b>Version:</b> 2.0.0
<b>Language:</b> Python 3
<b>Framework:</b> python-telegram-bot

Built for the Metrica project.
    """
    await query.message.reply_text(text, parse_mode='HTML')

async def _handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle help callback"""
    query = update.callback_query
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
    await query.message.reply_text(text, parse_mode='HTML')

@require_auth_callback
async def _handle_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle calendar callback - show calendar view"""
    query = update.callback_query
    
    # Create calendar starting with year selection
    calendar_markup, step = create_calendar()
    
    # Get the step text (Year, Month, or Day)
    step_text = LSTEP[step] if step in LSTEP else "date"
    
    text = f"<b>📅 Calendar</b>\n\nSelect {step_text}:"
    
    # Edit the message with calendar
    if query.message:
        await query.message.edit_text(
            text,
            reply_markup=calendar_markup,
            parse_mode='HTML'
        )

@require_auth_callback
async def _handle_calendar_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle calendar navigation (year/month/day selection)"""
    query = update.callback_query
    
    # Process calendar callback
    result, key, step = DetailedTelegramCalendar().process(query.data)
    
    if not result and key:
        # User is still selecting (year -> month -> day)
        step_text = LSTEP[step] if step in LSTEP else "date"
        text = f"<b>📅 Calendar</b>\n\nSelect {step_text}:"
        await query.message.edit_text(
            text,
            reply_markup=key,
            parse_mode='HTML'
        )
    elif result:
        # A date was selected
        selected_date = result.strftime("%Y-%m-%d")
        formatted_date = result.strftime("%B %d, %Y")
        
        logger.info(f"User {update.effective_user.id} selected date: {selected_date}")
        
        # TODO: Load orders for this date from database
        # For now, just show a message
        text = f"<b>📅 Selected Date: {formatted_date}</b>\n\n"
        text += "Orders for this date:\n"
        text += "• No orders found\n\n"
        text += "Would you like to add a new order?"
        
        # Create keyboard with back button and add order button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("➕ Add Order", callback_data=f'add_order_{selected_date}')],
            [InlineKeyboardButton("📅 Back to Calendar", callback_data='calendar')]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

@require_auth_callback
async def _handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings callback"""
    query = update.callback_query
    text = "<b>Settings</b>\n\nSettings panel coming soon!"
    await query.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.settings_menu(),
        parse_mode='HTML'
    )

@require_auth_callback  
async def _handle_reports(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reports callback"""
    query = update.callback_query
    text = "<b>Reports</b>\n\nReport generation coming soon!"
    await query.message.reply_text(text, parse_mode='HTML')

@require_auth_callback  
async def _handle_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tools callback"""
    query = update.callback_query
    text = "<b>Tools</b>\n\nAdditional tools coming soon!"
    await query.message.reply_text(text, parse_mode='HTML')