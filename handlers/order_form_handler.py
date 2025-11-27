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
    text += "Now, please select an employee:"
    
    await update.message.reply_text(
        text,
        parse_mode='HTML'
    )
    return await _show_employee_selection(update, context)

@require_auth
async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip description field"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['order_data']['description'] = ""
    
    return await _show_employee_selection(update, context)

@require_auth
async def _show_employee_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show employee selection from database"""
    from database.employee_service import EmployeeService
    
    employee_service = EmployeeService()
    employees = employee_service.get_all_employees()
    
    if not employees:
        text = "No employees found in the database.\n\n"
        text += "Please add employees first from the Employees menu."
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
        
        if update.callback_query:
            await update.callback_query.message.edit_text(
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
        return WAITING_EMPLOYEE_NAME
    
    text = "Please select an employee from the list:"
    
    # Create keyboard with employee buttons (max 2 per row)
    keyboard = []
    row = []
    for employee in employees:
        if employee.status == 'active':  # Only show active employees
            button_text = employee.employee_name
            if len(button_text) > 20:
                button_text = button_text[:17] + "..."
            row.append(InlineKeyboardButton(
                button_text,
                callback_data=f'select_employee_{employee.employee_id}'
            ))
            if len(row) == 2:
                keyboard.append(row)
                row = []
    
    if row:  # Add remaining buttons
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')])
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
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
    return WAITING_EMPLOYEE_NAME

@require_auth
async def receive_employee_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show employee selection (legacy - now redirects to selection)"""
    return await _show_employee_selection(update, context)

@require_auth
async def select_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle employee selection from callback"""
    query = update.callback_query
    await query.answer()
    
    # Extract employee_id from callback_data (format: select_employee_ID)
    callback_data = query.data
    if callback_data.startswith('select_employee_'):
        try:
            employee_id = int(callback_data.replace('select_employee_', ''))
            
            from database.employee_service import EmployeeService
            employee_service = EmployeeService()
            employee = employee_service.get_employee_by_id(employee_id)
            
            if not employee:
                await query.message.reply_text(
                    "Employee not found. Please try again.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]])
                )
                return WAITING_EMPLOYEE_NAME
            
            # Store employee info
            context.user_data['order_data']['employee_name'] = employee.employee_name
            context.user_data['order_data']['employee_id'] = employee.employee_id
            context.user_data['order_data']['employee_payment_method'] = employee.payment_method
            context.user_data['order_data']['employee_payment_value'] = employee.payment_value
            
            text = f"<b>Employee Selected:</b> {employee.employee_name}\n\n"
            text += "Now, please enter the income value (numeric value, e.g., 1000.50):"
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]]
            
            await query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            return WAITING_INCOME_VALUE
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing employee ID: {e}")
            await query.message.reply_text(
                "Error selecting employee. Please try again.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data='cancel_order_form')]])
            )
            return WAITING_EMPLOYEE_NAME
    
    return WAITING_EMPLOYEE_NAME

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
    """Save the order to database and calculate payroll if needed"""
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
        
        # Calculate and save payroll if employee has payment_method='in_percent'
        employee_payment_method = order_data.get('employee_payment_method')
        employee_id = order_data.get('employee_id')
        employee_name = order_data.get('employee_name', '')
        order_value = order_data.get('income_value', 0.0)
        
        payroll_message = ""
        if employee_payment_method == 'in_percent' and employee_id:
            payment_percent = order_data.get('employee_payment_value')
            if payment_percent and payment_percent > 0:
                calculated_amount = (order_value * payment_percent) / 100.0
                
                from database.payroll_service import PayrollService
                from database.models import Payroll
                
                payroll = Payroll(
                    employee_id=employee_id,
                    employee_name=employee_name,
                    order_id=order_id,
                    order_date=order_data.get('date', ''),
                    order_value=order_value,
                    payment_percent=payment_percent,
                    calculated_amount=calculated_amount
                )
                
                payroll_service = PayrollService()
                payroll_id = payroll_service.create_payroll(payroll)
                
                payroll_message = f"\n\n💰 <b>Payroll Calculated:</b>\n"
                payroll_message += f"Employee: {employee_name}\n"
                payroll_message += f"Payment: {payment_percent}% of {order_value:.2f} = {calculated_amount:.2f}"
                logger.info(f"Payroll {payroll_id} created for employee {employee_id} from order {order_id}")
        
        text = f"<b>✅ Order Created Successfully!</b>\n\n"
        text += f"<b>Order ID:</b> {order_id}\n"
        text += f"<b>Date:</b> {order_data.get('date')}\n"
        text += f"<b>Client:</b> {order_data.get('client_name')}\n"
        text += f"<b>Income:</b> {order_data.get('income_value', 0):.2f}\n"
        text += payroll_message
        text += "\n\nThe order has been saved to the database."
        
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

