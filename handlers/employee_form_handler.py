#!/usr/bin/env python3
"""
Employee form handler for collecting employee data step-by-step using ConversationHandler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import logging
from database.models import Employee
from database.employee_service import EmployeeService
from auth.decorators import require_auth

logger = logging.getLogger(__name__)

# Conversation states
(
    WAITING_EMPLOYEE_NAME,
    WAITING_PHONE_NUMBER,
    WAITING_PAYMENT_METHOD,
    WAITING_PAYMENT_VALUE,
    WAITING_DATE_STARTED,
    WAITING_EMAIL,
    WAITING_NOTES,
    CONFIRMING_EMPLOYEE
) = range(8)

@require_auth
async def start_employee_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the employee form"""
    query = update.callback_query
    
    if query:
        await query.answer()
        context.user_data['employee_data'] = {}
        
        text = "<b>➕ Add New Employee</b>\n\n"
        text += "Let's start by entering the employee name:"
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return WAITING_EMPLOYEE_NAME
    else:
        await update.message.reply_text("Please use the button to add an employee.")
        return ConversationHandler.END

@require_auth
async def receive_employee_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store employee name"""
    employee_name = update.message.text.strip()
    
    if not employee_name:
        await update.message.reply_text("Please enter a valid employee name:")
        return WAITING_EMPLOYEE_NAME
    
    context.user_data['employee_data']['employee_name'] = employee_name
    
    text = f"<b>Employee Name:</b> {employee_name}\n\n"
    text += "Now, please enter the phone number (optional):"
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data='skip_phone')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_PHONE_NUMBER

@require_auth
async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip phone number field"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['employee_data']['phone_number'] = ""
    
    text = "Phone number skipped.\n\n"
    text += "Now, please select the payment method:"
    
    keyboard = [
        [InlineKeyboardButton("👑 Owner", callback_data='payment_owner')],
        [InlineKeyboardButton("📊 In Percent", callback_data='payment_in_percent')],
        [InlineKeyboardButton("💰 Fixed Amount", callback_data='payment_fixed')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_PAYMENT_METHOD

@require_auth
async def receive_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store phone number"""
    phone_number = update.message.text.strip()
    context.user_data['employee_data']['phone_number'] = phone_number
    
    text = f"<b>Phone Number:</b> {phone_number}\n\n"
    text += "Now, please select the payment method:"
    
    keyboard = [
        [InlineKeyboardButton("👑 Owner", callback_data='payment_owner')],
        [InlineKeyboardButton("📊 In Percent", callback_data='payment_in_percent')],
        [InlineKeyboardButton("💰 Fixed Amount", callback_data='payment_fixed')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_PAYMENT_METHOD

@require_auth
async def receive_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive payment method selection"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    if callback_data == 'payment_owner':
        payment_method = 'owner'
        payment_value = None
        context.user_data['employee_data']['payment_method'] = payment_method
        context.user_data['employee_data']['payment_value'] = payment_value
        
        # Skip payment value for owner
        text = f"<b>Payment Method:</b> Owner\n\n"
        text += "Now, please enter the date when the employee started (YYYY-MM-DD format):"
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return WAITING_DATE_STARTED
    elif callback_data == 'payment_in_percent':
        payment_method = 'in_percent'
        context.user_data['employee_data']['payment_method'] = payment_method
        
        text = f"<b>Payment Method:</b> In Percent\n\n"
        text += "Please enter the percentage (0-100, e.g., 30 for 30%):"
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return WAITING_PAYMENT_VALUE
    elif callback_data == 'payment_fixed':
        payment_method = 'fixed'
        context.user_data['employee_data']['payment_method'] = payment_method
        
        text = f"<b>Payment Method:</b> Fixed Amount\n\n"
        text += "Please enter the fixed payment amount (e.g., 5000.00):"
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return WAITING_PAYMENT_VALUE

@require_auth
async def receive_payment_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store payment value"""
    try:
        payment_value = float(update.message.text.strip().replace(',', '.'))
        payment_method = context.user_data['employee_data'].get('payment_method', 'fixed')
        
        if payment_method == 'in_percent':
            if payment_value < 0 or payment_value > 100:
                await update.message.reply_text("Please enter a percentage between 0 and 100:")
                return WAITING_PAYMENT_VALUE
        elif payment_method == 'fixed':
            if payment_value < 0:
                await update.message.reply_text("Please enter a positive value:")
                return WAITING_PAYMENT_VALUE
        
        context.user_data['employee_data']['payment_value'] = payment_value
        
        text = f"<b>Payment Value:</b> {payment_value:.2f}"
        if payment_method == 'in_percent':
            text += "%"
        text += "\n\n"
        text += "Now, please enter the date when the employee started (YYYY-MM-DD format):"
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return WAITING_DATE_STARTED
    except ValueError:
        payment_method = context.user_data['employee_data'].get('payment_method', 'fixed')
        if payment_method == 'in_percent':
            await update.message.reply_text("Please enter a valid percentage (0-100):")
        else:
            await update.message.reply_text("Please enter a valid numeric value (e.g., 5000.00):")
        return WAITING_PAYMENT_VALUE

@require_auth
async def receive_date_started(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store date started"""
    date_started = update.message.text.strip()
    
    # Basic date validation (YYYY-MM-DD format)
    try:
        datetime.strptime(date_started, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text("Please enter a valid date in YYYY-MM-DD format (e.g., 2024-01-15):")
        return WAITING_DATE_STARTED
    
    context.user_data['employee_data']['date_started'] = date_started
    
    text = f"<b>Date Started:</b> {date_started}\n\n"
    text += "Now, please enter the email address (optional):"
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data='skip_email')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_EMAIL

@require_auth
async def skip_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip email field"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['employee_data']['email'] = ""
    
    text = "Email skipped.\n\n"
    text += "Now, please enter any additional notes (optional):"
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data='skip_notes')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_NOTES

@require_auth
async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store email"""
    email = update.message.text.strip()
    context.user_data['employee_data']['email'] = email
    
    text = f"<b>Email:</b> {email}\n\n"
    text += "Now, please enter any additional notes (optional):"
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data='skip_notes')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return WAITING_NOTES

@require_auth
async def skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip notes field"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['employee_data']['notes'] = ""
    
    return await _show_confirmation(update, context)

@require_auth
async def receive_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and store notes"""
    notes = update.message.text.strip()
    context.user_data['employee_data']['notes'] = notes
    
    return await _show_confirmation(update, context)

async def _show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show employee confirmation"""
    employee_data = context.user_data.get('employee_data', {})
    
    text = "<b>👥 Employee Summary</b>\n\n"
    text += f"👤 <b>Name:</b> {employee_data.get('employee_name', 'N/A')}\n"
    
    phone = employee_data.get('phone_number', '')
    if phone:
        text += f"📞 <b>Phone:</b> {phone}\n"
    
    payment_method = employee_data.get('payment_method', 'fixed')
    payment_value = employee_data.get('payment_value')
    
    if payment_method == 'owner':
        text += f"💼 <b>Payment:</b> Owner\n"
    elif payment_method == 'in_percent':
        text += f"💼 <b>Payment:</b> {payment_value:.2f}%\n"
    elif payment_method == 'fixed':
        text += f"💼 <b>Payment:</b> Fixed - {payment_value:.2f}\n"
    
    text += f"📅 <b>Date Started:</b> {employee_data.get('date_started', 'N/A')}\n"
    
    email = employee_data.get('email', '')
    if email:
        text += f"📧 <b>Email:</b> {email}\n"
    
    notes = employee_data.get('notes', '')
    if notes:
        text += f"📝 <b>Notes:</b> {notes}\n"
    
    text += "\nPlease confirm to save this employee:"
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_employee')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_employee_form')]
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
    
    return CONFIRMING_EMPLOYEE

@require_auth
async def confirm_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save the employee to database"""
    query = update.callback_query
    await query.answer()
    
    employee_data = context.user_data.get('employee_data', {})
    
    try:
        # Create Employee object
        employee = Employee(
            employee_name=employee_data.get('employee_name', ''),
            phone_number=employee_data.get('phone_number', ''),
            payment_method=employee_data.get('payment_method', 'fixed'),
            payment_value=employee_data.get('payment_value'),
            date_started=employee_data.get('date_started', ''),
            email=employee_data.get('email', ''),
            status='active',
            notes=employee_data.get('notes', '')
        )
        
        # Save to database
        employee_service = EmployeeService()
        employee_id = employee_service.create_employee(employee)
        
        text = f"<b>✅ Employee Created Successfully!</b>\n\n"
        text += f"<b>Employee ID:</b> {employee_id}\n"
        text += f"<b>Name:</b> {employee_data.get('employee_name')}\n"
        text += f"<b>Date Started:</b> {employee_data.get('date_started')}\n\n"
        text += "The employee has been saved to the database."
        
        keyboard = [
            [InlineKeyboardButton("👥 Back to Employees", callback_data='employees')],
            [InlineKeyboardButton("➕ Add Another Employee", callback_data='add_employee')]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
        # Clear user data
        context.user_data.pop('employee_data', None)
        
        logger.info(f"Employee {employee_id} created successfully by user {update.effective_user.id}")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error saving employee: {e}")
        await query.message.reply_text(
            "❌ Error saving employee. Please try again.",
            parse_mode='HTML'
        )
        return ConversationHandler.END

@require_auth
async def cancel_employee_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the employee form"""
    query = update.callback_query
    if query:
        await query.answer()
        await query.message.edit_text(
            "❌ Employee creation cancelled.",
            reply_markup=None
        )
    else:
        await update.message.reply_text("❌ Employee creation cancelled.")
    
    # Clear user data
    context.user_data.pop('employee_data', None)
    
    return ConversationHandler.END

async def cancel_employee_form_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel command from message"""
    await cancel_employee_form(update, context)
    return ConversationHandler.END

