#!/usr/bin/env python3
"""
Order form handler for collecting order data step-by-step using ConversationHandler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import logging
from database.models import Order
from database.order_service import OrderService
from auth.decorators import require_auth

logger = logging.getLogger(__name__)

# Conversation states
(
    WAITING_CLIENT_NAME,
    WAITING_DESCRIPTION,
    WAITING_EMPLOYEE_NAME,
    WAITING_INCOME_VALUE,
    WAITING_CLIENT_CONTACT,
    CONFIRMING_ORDER
) = range(6)

@require_auth
async def start_order_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the order form - extract date from callback data"""
    query = update.callback_query
    
    if query:
        await query.answer()
        # Extract date from callback_data (format: add_order_YYYY-MM-DD)
        callback_data = query.data
        if callback_data.startswith('add_order_'):
            date_str = callback_data.replace('add_order_', '')
            context.user_data['order_date'] = date_str
            context.user_data['order_data'] = {'date': date_str}
            
            text = f"<b>➕ Add New Order</b>\n\n"
            text += f"📅 <b>Date:</b> {date_str}\n\n"
            text += "Let's start by entering the client name:"
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
            
            await query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            return WAITING_CLIENT_NAME
    else:
        # Fallback if called from message
        await update.message.reply_text("Please use the calendar to select a date first.")
        return ConversationHandler.END

@require_auth
async def receive_client_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store client name"""
    client_name = update.message.text.strip()
    
    if not client_name:
        await update.message.reply_text("Please enter a valid client name:")
        return WAITING_CLIENT_NAME
    
    context.user_data['order_data']['client_name'] = client_name
    
    text = f"<b>Client Name:</b> {client_name}\n\n"
    text += "Now, please enter a description for this order:"
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data='skip_description')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_DESCRIPTION

@require_auth
async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store description"""
    description = update.message.text.strip()
    context.user_data['order_data']['description'] = description
    
    text = f"<b>Description:</b> {description}\n\n"
    text += "Now, please enter the employee name:"
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_EMPLOYEE_NAME

@require_auth
async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip description field"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['order_data']['description'] = ""
    
    text = "Description skipped.\n\n"
    text += "Now, please enter the employee name:"
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_EMPLOYEE_NAME

@require_auth
async def receive_employee_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store employee name"""
    employee_name = update.message.text.strip()
    
    if not employee_name:
        await update.message.reply_text("Please enter a valid employee name:")
        return WAITING_EMPLOYEE_NAME
    
    context.user_data['order_data']['employee_name'] = employee_name
    
    text = f"<b>Employee Name:</b> {employee_name}\n\n"
    text += "Now, please enter the income value (numeric value, e.g., 1000.50):"
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_INCOME_VALUE

@require_auth
async def receive_income_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store income value"""
    try:
        income_value = float(update.message.text.strip().replace(',', '.'))
        
        if income_value < 0:
            await update.message.reply_text("Please enter a positive value:")
            return WAITING_INCOME_VALUE
        
        context.user_data['order_data']['income_value'] = income_value
        
        text = f"<b>Income Value:</b> {income_value:.2f}\n\n"
        text += "Now, please enter client contact (phone or email) - optional:"
        
        keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data='skip_contact')],
                    [InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return WAITING_CLIENT_CONTACT
    except ValueError:
        await update.message.reply_text("Please enter a valid numeric value (e.g., 1000.50):")
        return WAITING_INCOME_VALUE

@require_auth
async def receive_client_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store client contact"""
    client_contact = update.message.text.strip()
    context.user_data['order_data']['client_contact'] = client_contact
    
    return await _show_confirmation(update, context)

@require_auth
async def skip_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip client contact field"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['order_data']['client_contact'] = ""
    
    return await _show_confirmation(update, context)

async def _show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show order confirmation"""
    order_data = context.user_data.get('order_data', {})
    
    text = "<b>📋 Order Summary</b>\n\n"
    text += f"📅 <b>Date:</b> {order_data.get('date', 'N/A')}\n"
    text += f"👤 <b>Client:</b> {order_data.get('client_name', 'N/A')}\n"
    text += f"📝 <b>Description:</b> {order_data.get('description', 'None')}\n"
    text += f"👨‍💼 <b>Employee:</b> {order_data.get('employee_name', 'N/A')}\n"
    text += f"💰 <b>Income:</b> {order_data.get('income_value', 0):.2f}\n"
    
    contact = order_data.get('client_contact', '')
    if contact:
        text += f"📞 <b>Contact:</b> {contact}\n"
    
    text += "\nPlease confirm to save this order:"
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_order')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]
    ]
    
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    return CONFIRMING_ORDER

@require_auth
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save the order to database"""
    query = update.callback_query
    await query.answer()
    
    order_data = context.user_data.get('order_data', {})
    
    try:
        # Create Order object
        order = Order(
            client_name=order_data.get('client_name', ''),
            description=order_data.get('description', ''),
            date=order_data.get('date', ''),
            employee_name=order_data.get('employee_name', ''),
            income_value=order_data.get('income_value', 0.0),
            status='pending',
            client_contact=order_data.get('client_contact', '')
        )
        
        # Save to database
        order_service = OrderService()
        order_id = order_service.create_order(order)
        
        text = f"<b>✅ Order Created Successfully!</b>\n\n"
        text += f"<b>Order ID:</b> {order_id}\n"
        text += f"<b>Date:</b> {order_data.get('date')}\n"
        text += f"<b>Client:</b> {order_data.get('client_name')}\n"
        text += f"<b>Income:</b> {order_data.get('income_value', 0):.2f}\n\n"
        text += "The order has been saved to the database."
        
        keyboard = [
            [InlineKeyboardButton("📅 Back to Calendar", callback_data='calendar')],
            [InlineKeyboardButton("➕ Add Another Order", callback_data=f"add_order_{order_data.get('date')}")]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
        # Clear user data
        context.user_data.pop('order_data', None)
        context.user_data.pop('order_date', None)
        
        logger.info(f"Order {order_id} created successfully by user {update.effective_user.id}")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error saving order: {e}")
        await query.message.reply_text(
            "❌ Error saving order. Please try again.",
            parse_mode='HTML'
        )
        return ConversationHandler.END

@require_auth
async def cancel_order_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the order form"""
    query = update.callback_query
    if query:
        await query.answer()
        await query.message.edit_text(
            "❌ Order creation cancelled.",
            reply_markup=None
        )
    else:
        await update.message.reply_text("❌ Order creation cancelled.")
    
    # Clear user data
    context.user_data.pop('order_data', None)
    context.user_data.pop('order_date', None)
    
    return ConversationHandler.END

async def cancel_order_form_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel command from message"""
    await cancel_order_form(update, context)
    return ConversationHandler.END

