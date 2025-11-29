#!/usr/bin/env python3
"""
Callback handler for processing inline keyboard callbacks using python-telegram-bot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.keyboards import KeyboardTemplates
from utils.calendar_utils import create_calendar
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime
import logging
import json
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
        elif callback_data == 'orders':
            await _handle_orders(update, context)
        elif callback_data == 'order_add':
            # Show calendar to select date for new order
            await _handle_calendar(update, context)
        elif callback_data == 'order_list' or callback_data.startswith('order_list_page_'):
            await _handle_order_list(update, context)
        elif callback_data == 'add_employee':
            # This will be handled by ConversationHandler
            pass
        elif callback_data == 'employee_list' or callback_data.startswith('employee_list_page_'):
            await _handle_employee_list(update, context)
        elif callback_data == 'payroll_list' or callback_data.startswith('payroll_list_page_'):
            await _handle_payroll_list(update, context)
        elif callback_data.startswith('payroll_detail_') or callback_data.startswith('payroll_mark_paid_'):
            await _handle_payroll_detail(update, context)
        elif callback_data == 'settings':
            await _handle_settings(update, context)
        elif callback_data == 'employees':
            await _handle_employees(update, context)
        elif callback_data == 'income_expense':
            await _handle_income_expense(update, context)
        elif callback_data == 'income_expense_table' or callback_data.startswith('income_expense_table_page_'):
            await _handle_income_expense_table(update, context)
        elif callback_data == 'income_expense_analysis':
            await _handle_income_expense_analysis(update, context)
        else:
            # Try to handle as calendar navigation callback
            # Calendar callbacks from telegram_bot_calendar start with 'cbcal_'
            if callback_data.startswith('cbcal_'):
                # It's a calendar callback - handle it directly
                try:
                    await _handle_calendar_navigation(update, context)
                except Exception as e:
                    logger.error(f"Error handling calendar navigation: {e}")
                    await query.message.reply_text("Sorry, something went wrong with the calendar. Please try again.")
            else:
                # Not a calendar callback - might be add_order_* or other future callbacks
                # Check for add_order pattern or ConversationHandler callbacks - skip these
                if (callback_data.startswith('add_order_') or 
                    callback_data.startswith('select_employee_') or
                    callback_data in ['cancel_order_form', 'skip_description', 'skip_contact', 'confirm_order',
                                     'cancel_employee_form', 'skip_phone', 'skip_email', 'skip_notes', 'confirm_employee',
                                     'payment_owner', 'payment_in_percent', 'payment_fixed']):
                    # These are handled by ConversationHandler - don't process here
                    pass
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

async def _handle_about(query) -> None:
    """Handle about callback"""
    text = """
<b>Metrica Bot</b>

A simple Telegram bot built with Python and python-telegram-bot framework.

<b>Version:</b> 2.0.0
<b>Language:</b> Python 3
<b>Framework:</b> python-telegram-bot

Built for the Metrica project.
    """
    await query.message.reply_text(text, parse_mode='HTML')

async def _handle_help(query) -> None:
    """Handle help callback"""
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
    await query.answer()
    
    # Create calendar
    calendar_markup, step = create_calendar()
    
    # Get the step text
    step_text = LSTEP[step] if step in LSTEP else "date"
    
    text = f"<b>📅 Calendar</b>\n\nSelect {step_text}:"
    
    # Add "Back to Menu" button to the calendar keyboard (same approach as navigation)
    if query.message:
        # Extract rows from the calendar markup and add the back button
        rows = []
        if isinstance(calendar_markup, InlineKeyboardMarkup):
            # Convert tuple of tuples to list of lists
            for row in calendar_markup.inline_keyboard:
                rows.append(list(row))
        elif isinstance(calendar_markup, str):
            # Parse the JSON string to get the keyboard structure
            try:
                keyboard_data = json.loads(calendar_markup)
                if 'inline_keyboard' in keyboard_data:
                    # Reconstruct InlineKeyboardButton objects from the JSON data
                    for row_data in keyboard_data['inline_keyboard']:
                        if row_data:  # Skip empty rows
                            row = []
                            for button_data in row_data:
                                button = InlineKeyboardButton(
                                    text=button_data['text'],
                                    callback_data=button_data['callback_data']
                                )
                                row.append(button)
                            if row:  # Only add non-empty rows
                                rows.append(row)
                else:
                    logger.warning(f"JSON calendar_markup doesn't contain 'inline_keyboard': {calendar_markup[:100]}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse calendar_markup as JSON: {e}, markup: {str(calendar_markup)[:100]}")
            except Exception as e:
                logger.error(f"Error parsing calendar keyboard: {e}")
        else:
            # If calendar_markup is not InlineKeyboardMarkup or string, try to handle it
            logger.warning(f"Calendar markup is not InlineKeyboardMarkup or string: {type(calendar_markup)}")
            # Try to use it as-is if it has inline_keyboard attribute
            if hasattr(calendar_markup, 'inline_keyboard'):
                for row in calendar_markup.inline_keyboard:
                    rows.append(list(row))
        
        # Append "Back to Menu" as its own row
        rows.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="menu")])
        
        # Create new keyboard with the back button
        new_keyboard = InlineKeyboardMarkup(rows)
        
        # Edit the message with the calendar and back button in one keyboard
        await query.message.edit_text(
            text,
            reply_markup=new_keyboard,
            parse_mode='HTML'
        )

@require_auth_callback
async def _handle_calendar_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle calendar navigation (year/month/day selection)"""
    query = update.callback_query
    
    # Process calendar callback
    calendar = DetailedTelegramCalendar()
    result, key, step = calendar.process(query.data)
    
    # Check if we have a valid keyboard (InlineKeyboardMarkup) and no result yet
    if not result and isinstance(key, InlineKeyboardMarkup):
        # User is still selecting (year -> month -> day)
        step_text = LSTEP[step] if step in LSTEP else "date"
        text = f"<b>📅 Calendar</b>\n\nSelect {step_text}:"

        # Extract rows from the keyboard and convert tuples to lists
        rows = []
        for row in key.inline_keyboard:
            rows.append(list(row))  # Convert tuple to list

        # Append "Back to Menu" as its own row
        rows.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="menu")])
        
        # Create new keyboard with the back button
        new_keyboard = InlineKeyboardMarkup(rows)
        await query.message.edit_text(
            text,
            reply_markup=new_keyboard,
            parse_mode='HTML'
        )
    elif not result and key:
        # key exists but is not an InlineKeyboardMarkup
        # It might be a JSON string representation of the keyboard
        rows = []
        try:
            if isinstance(key, str):
                # Parse the JSON string to get the keyboard structure
                keyboard_data = json.loads(key)
                if 'inline_keyboard' in keyboard_data:
                    # Reconstruct InlineKeyboardButton objects from the JSON data
                    for row_data in keyboard_data['inline_keyboard']:
                        if row_data:  # Skip empty rows
                            row = []
                            for button_data in row_data:
                                button = InlineKeyboardButton(
                                    text=button_data['text'],
                                    callback_data=button_data['callback_data']
                                )
                                row.append(button)
                            if row:  # Only add non-empty rows
                                rows.append(row)
                else:
                    logger.warning(f"JSON key doesn't contain 'inline_keyboard': {key[:100]}")
            else:
                logger.warning(f"Unexpected key type: {type(key)}, value: {str(key)[:100]}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse key as JSON: {e}, key: {str(key)[:100]}")
        except Exception as e:
            logger.error(f"Error parsing calendar keyboard: {e}")
        
        # If we successfully parsed rows, display the calendar
        if rows:
            step_text = LSTEP[step] if step in LSTEP else "date"
            text = f"<b>📅 Calendar</b>\n\nSelect {step_text}:"
            
            # Append "Back to Menu" as its own row
            rows.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="menu")])
            
            # Create new keyboard with the back button
            new_keyboard = InlineKeyboardMarkup(rows)
            await query.message.edit_text(
                text,
                reply_markup=new_keyboard,
                parse_mode='HTML'
            )
        else:
            # Fallback: show error message
            logger.error("Failed to parse calendar keyboard, showing error message")
            await query.message.reply_text(
                "Sorry, there was an error displaying the calendar navigation. Please try selecting the calendar again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📅 Back to Calendar", callback_data="calendar")],
                    [InlineKeyboardButton("🏠 Back to Menu", callback_data="menu")]
                ])
            )
    elif result:
        # A date was selected
        selected_date = result.strftime("%Y-%m-%d")
        formatted_date = result.strftime("%B %d, %Y")
        
        logger.info(f"User {update.effective_user.id} selected date: {selected_date}")
        
        # Load orders for this date from database
        from database.order_service import OrderService
        order_service = OrderService()
        orders = order_service.get_orders_by_date(selected_date)
        
        text = f"<b>📅 Selected Date: {formatted_date}</b>\n\n"
        
        if orders:
            text += f"<b>Orders for this date ({len(orders)}):</b>\n"
            for order in orders:
                text += f"• <b>#{order.order_id}</b> - {order.client_name} - {order.income_value:.2f}\n"
            text += "\n"
        else:
            text += "Orders for this date:\n"
            text += "• No orders found\n\n"
        
        text += "Would you like to add a new order?"
        
        # Create keyboard with back button, add order button, and menu button
        keyboard = [
            [InlineKeyboardButton("➕ Add Order", callback_data=f'add_order_{selected_date}')],
            [InlineKeyboardButton("📅 Back to Calendar", callback_data='calendar')],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data='menu')]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

@require_auth_callback
async def _handle_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle orders callback"""
    query = update.callback_query
    text = "<b>📋 Orders</b>\n\nManage your orders:"
    await query.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.orders_menu(),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_order_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle order list callback with pagination"""
    query = update.callback_query
    await query.answer()
    
    # Parse page number from callback_data
    callback_data = query.data
    page = 0
    if callback_data.startswith('order_list_page_'):
        try:
            page = int(callback_data.replace('order_list_page_', ''))
        except ValueError:
            page = 0
    
    # Pagination settings
    ORDERS_PER_PAGE = 5
    offset = page * ORDERS_PER_PAGE
    
    # Get orders from database
    from database.order_service import OrderService
    order_service = OrderService()
    orders = order_service.get_all_orders(limit=ORDERS_PER_PAGE, offset=offset)
    total_orders = order_service.get_orders_count()
    total_pages = (total_orders + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE if total_orders > 0 else 1
    
    # Build the message with monospace table
    text = "<b>📋 Orders List</b>\n\n"
    
    if not orders:
        text += "No orders found."
    else:
        # Format as monospace table
        text += "```\n"
        text += f"{'ID':<6} {'Date':<12} {'Client':<20} {'Income':<12} {'Status':<10}\n"
        text += "-" * 70 + "\n"
        
        for order in orders:
            # Truncate long names
            client_name = order.client_name[:18] if len(order.client_name) > 18 else order.client_name
            date_str = order.date[:10] if len(order.date) > 10 else order.date
            income_str = f"{order.income_value:.2f}"
            status_str = order.status[:8] if len(order.status) > 8 else order.status
            
            text += f"{order.order_id:<6} {date_str:<12} {client_name:<20} {income_str:<12} {status_str:<10}\n"
        
        text += "```\n"
        text += f"\n<b>Page {page + 1} of {total_pages}</b> | <b>Total: {total_orders} orders</b>"
    
    # Build pagination keyboard
    keyboard = []
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f'order_list_page_{page - 1}'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f'order_list_page_{page + 1}'))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Back button
    keyboard.append([InlineKeyboardButton("← Back to Orders", callback_data='orders')])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings callback (legacy - kept for backward compatibility)"""
    query = update.callback_query
    text = "<b>Settings</b>\n\nSettings panel coming soon!"
    await query.message.reply_text(
        text,
        parse_mode='HTML'
    )

@require_auth_callback  
async def _handle_employees(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle employees callback"""
    query = update.callback_query
    text = "<b>👥 Employees</b>\n\nManage your employees:"
    await query.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.employees_menu(),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_employee_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle employee list callback with pagination"""
    query = update.callback_query
    await query.answer()
    
    # Parse page number from callback_data
    callback_data = query.data
    page = 0
    if callback_data.startswith('employee_list_page_'):
        try:
            page = int(callback_data.replace('employee_list_page_', ''))
        except ValueError:
            page = 0
    
    # Pagination settings
    EMPLOYEES_PER_PAGE = 5
    offset = page * EMPLOYEES_PER_PAGE
    
    # Get employees from database
    from database.employee_service import EmployeeService
    employee_service = EmployeeService()
    employees = employee_service.get_all_employees(limit=EMPLOYEES_PER_PAGE, offset=offset)
    total_employees = employee_service.get_employees_count()
    total_pages = (total_employees + EMPLOYEES_PER_PAGE - 1) // EMPLOYEES_PER_PAGE if total_employees > 0 else 1
    
    # Build the message with monospace table
    text = "<b>👥 Employees List</b>\n\n"
    
    if not employees:
        text += "No employees found."
    else:
        # Format as monospace table
        text += "```\n"
        text += f"{'ID':<6} {'Name':<20} {'Payment':<15} {'Status':<10} {'Started':<12}\n"
        text += "-" * 75 + "\n"
        
        for employee in employees:
            # Truncate long names
            name = employee.employee_name[:18] if len(employee.employee_name) > 18 else employee.employee_name
            date_str = employee.date_started[:10] if len(employee.date_started) > 10 else employee.date_started
            
            # Format payment method
            payment_str = ""
            if employee.payment_method == 'owner':
                payment_str = "Owner"
            elif employee.payment_method == 'in_percent':
                payment_str = f"{employee.payment_value:.1f}%" if employee.payment_value else "N/A"
            elif employee.payment_method == 'fixed':
                payment_str = f"${employee.payment_value:.0f}" if employee.payment_value else "N/A"
            payment_str = payment_str[:13] if len(payment_str) > 13 else payment_str
            
            status_str = employee.status[:8] if len(employee.status) > 8 else employee.status
            
            text += f"{employee.employee_id:<6} {name:<20} {payment_str:<15} {status_str:<10} {date_str:<12}\n"
        
        text += "```\n"
        text += f"\n<b>Page {page + 1} of {total_pages}</b> | <b>Total: {total_employees} employees</b>"
    
    # Build pagination keyboard
    keyboard = []
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f'employee_list_page_{page - 1}'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f'employee_list_page_{page + 1}'))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Back button
    keyboard.append([InlineKeyboardButton("← Back to Employees", callback_data='employees')])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_payroll_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payroll list callback with pagination - shows pending payrolls"""
    query = update.callback_query
    await query.answer()
    
    # Parse page number from callback_data
    callback_data = query.data
    page = 0
    if callback_data.startswith('payroll_list_page_'):
        try:
            page = int(callback_data.replace('payroll_list_page_', ''))
        except ValueError:
            page = 0
    
    # Pagination settings
    PAYROLL_PER_PAGE = 5
    offset = page * PAYROLL_PER_PAGE
    
    # Get pending payrolls from database
    from database.payroll_service import PayrollService
    payroll_service = PayrollService()
    all_payrolls = payroll_service.get_payrolls_by_status('pending')
    
    # Calculate pagination
    total_entries = len(all_payrolls)
    total_pages = (total_entries + PAYROLL_PER_PAGE - 1) // PAYROLL_PER_PAGE if total_entries > 0 else 1
    
    # Get paginated results
    start_idx = offset
    end_idx = min(offset + PAYROLL_PER_PAGE, total_entries)
    paginated_payrolls = all_payrolls[start_idx:end_idx]
    
    # Build the message
    text = "<b>💰 Pending Payroll Payments</b>\n\n"
    
    if not paginated_payrolls:
        text += "No pending payroll payments found."
    else:
        # Format as monospace table
        text += "```\n"
        text += f"{'ID':<6} {'Employee':<18} {'Order':<8} {'Amount':<12} {'Date':<12}\n"
        text += "-" * 60 + "\n"
        
        for payroll in paginated_payrolls:
            employee_name = payroll.employee_name[:16] if len(payroll.employee_name) > 16 else payroll.employee_name
            order_id = str(payroll.order_id)
            amount = f"{payroll.calculated_amount:.2f}"
            date_str = payroll.order_date[:10] if len(payroll.order_date) > 10 else payroll.order_date
            
            text += f"{payroll.payroll_id:<6} {employee_name:<18} {order_id:<8} {amount:<12} {date_str:<12}\n"
        
        text += "```\n"
        text += f"\n<b>Page {page + 1} of {total_pages}</b> | <b>Total: {total_entries} pending payments</b>"
        text += "\n\nClick on a payroll ID to mark it as paid."
    
    # Build keyboard with payroll buttons
    keyboard = []
    
    # Add buttons for each payroll entry (2 per row)
    row = []
    for payroll in paginated_payrolls:
        button_text = f"#{payroll.payroll_id} - {payroll.employee_name[:15]}"
        if len(button_text) > 30:
            button_text = button_text[:27] + "..."
        row.append(InlineKeyboardButton(
            button_text,
            callback_data=f'payroll_detail_{payroll.payroll_id}'
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:  # Add remaining buttons
        keyboard.append(row)
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f'payroll_list_page_{page - 1}'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f'payroll_list_page_{page + 1}'))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Back button
    keyboard.append([InlineKeyboardButton("← Back to Employees", callback_data='employees')])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_payroll_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payroll detail view and mark as paid"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Check if marking as paid
    if callback_data.startswith('payroll_mark_paid_'):
        try:
            payroll_id = int(callback_data.replace('payroll_mark_paid_', ''))
            
            from database.payroll_service import PayrollService
            payroll_service = PayrollService()
            
            # Mark as paid and create expense
            success = payroll_service.mark_payroll_as_paid(payroll_id)
            
            if success:
                payroll = payroll_service.get_payroll_by_id(payroll_id)
                text = f"<b>✅ Payroll Marked as Paid</b>\n\n"
                text += f"<b>Payroll ID:</b> {payroll.payroll_id}\n"
                text += f"<b>Employee:</b> {payroll.employee_name}\n"
                text += f"<b>Order ID:</b> {payroll.order_id}\n"
                text += f"<b>Amount:</b> {payroll.calculated_amount:.2f}\n"
                text += f"<b>Status:</b> ✅ Paid\n\n"
                text += f"An expense entry has been created for this payment."
                
                keyboard = [
                    [InlineKeyboardButton("← Back to Payroll List", callback_data='payroll_list')],
                    [InlineKeyboardButton("← Back to Employees", callback_data='employees')]
                ]
                
                await query.message.edit_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
            else:
                await query.message.reply_text(
                    "❌ Error marking payroll as paid. Please try again.",
                    parse_mode='HTML'
                )
        except (ValueError, Exception) as e:
            logger.error(f"Error marking payroll as paid: {e}")
            await query.message.reply_text(
                "❌ Error processing request. Please try again.",
                parse_mode='HTML'
            )
        return
    
    # Show payroll detail
    if callback_data.startswith('payroll_detail_'):
        try:
            payroll_id = int(callback_data.replace('payroll_detail_', ''))
            
            from database.payroll_service import PayrollService
            payroll_service = PayrollService()
            payroll = payroll_service.get_payroll_by_id(payroll_id)
            
            if not payroll:
                await query.message.reply_text(
                    "❌ Payroll not found.",
                    parse_mode='HTML'
                )
                return
            
            # Build detail message
            text = f"<b>💰 Payroll Details</b>\n\n"
            text += f"<b>Payroll ID:</b> {payroll.payroll_id}\n"
            text += f"<b>Employee:</b> {payroll.employee_name}\n"
            text += f"<b>Order ID:</b> {payroll.order_id}\n"
            text += f"<b>Order Date:</b> {payroll.order_date}\n"
            text += f"<b>Order Value:</b> {payroll.order_value:.2f}\n"
            if payroll.payment_percent:
                text += f"<b>Payment Percent:</b> {payroll.payment_percent}%\n"
            text += f"<b>Calculated Amount:</b> {payroll.calculated_amount:.2f}\n"
            text += f"<b>Status:</b> "
            
            if payroll.status == 'pending':
                text += "⏳ Pending"
            elif payroll.status == 'paid':
                text += "✅ Paid"
            else:
                text += payroll.status
            
            # Build keyboard
            keyboard = []
            
            # Add mark as paid button if status is pending
            if payroll.status == 'pending':
                keyboard.append([
                    InlineKeyboardButton("✅ Mark as Paid", callback_data=f'payroll_mark_paid_{payroll_id}')
                ])
            
            keyboard.append([InlineKeyboardButton("← Back to Payroll List", callback_data='payroll_list')])
            keyboard.append([InlineKeyboardButton("← Back to Employees", callback_data='employees')])
            
            await query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except (ValueError, Exception) as e:
            logger.error(f"Error showing payroll detail: {e}")
            await query.message.reply_text(
                "❌ Error loading payroll details. Please try again.",
                parse_mode='HTML'
            )

@require_auth_callback
async def _handle_income_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle income & expense callback"""
    query = update.callback_query
    text = "<b>💰 Incomes & Expenses</b>\n\nManage your financial transactions:"
    await query.message.reply_text(
        text,
        reply_markup=KeyboardTemplates.income_expense_menu(),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_income_expense_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle income & expense table callback with pagination"""
    query = update.callback_query
    await query.answer()
    
    # Parse page number from callback_data
    callback_data = query.data
    page = 0
    if callback_data.startswith('income_expense_table_page_'):
        try:
            page = int(callback_data.replace('income_expense_table_page_', ''))
        except ValueError:
            page = 0
    
    # Pagination settings
    TRANSACTIONS_PER_PAGE = 10
    offset = page * TRANSACTIONS_PER_PAGE
    
    # Get transactions from database
    from database.income_expense_service import IncomeExpenseService
    income_expense_service = IncomeExpenseService()
    transactions = income_expense_service.get_all_transactions(limit=TRANSACTIONS_PER_PAGE, offset=offset)
    total_transactions = income_expense_service.get_transactions_count()
    total_pages = (total_transactions + TRANSACTIONS_PER_PAGE - 1) // TRANSACTIONS_PER_PAGE if total_transactions > 0 else 1
    
    # Build the message with monospace table
    text = "<b>📊 Incomes & Expenses Table</b>\n\n"
    
    if not transactions:
        text += "No transactions found."
    else:
        # Format as monospace table
        text += "```\n"
        text += f"{'ID':<6} {'Type':<8} {'Date':<12} {'Value':<12} {'Description':<25}\n"
        text += "-" * 75 + "\n"
        
        for transaction in transactions:
            transaction_id = str(transaction.transaction_id)
            transaction_type = "Income" if transaction.transaction_type == 'income' else "Expense"
            date_str = transaction.created_at[:10] if len(transaction.created_at) > 10 else transaction.created_at
            value_str = f"{transaction.value:.2f}"
            description = transaction.description[:23] if len(transaction.description) > 23 else transaction.description
            if not description:
                description = transaction.source or "N/A"
            
            # Add + for income, - for expense
            value_display = f"+{value_str}" if transaction.transaction_type == 'income' else f"-{value_str}"
            
            text += f"{transaction_id:<6} {transaction_type:<8} {date_str:<12} {value_display:<12} {description:<25}\n"
        
        text += "```\n"
        text += f"\n<b>Page {page + 1} of {total_pages}</b> | <b>Total: {total_transactions} transactions</b>"
    
    # Build pagination keyboard
    keyboard = []
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f'income_expense_table_page_{page - 1}'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f'income_expense_table_page_{page + 1}'))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Back button
    keyboard.append([InlineKeyboardButton("← Back to Incomes & Expenses", callback_data='income_expense')])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

@require_auth_callback
async def _handle_income_expense_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle income & expense analysis callback"""
    query = update.callback_query
    await query.answer()
    
    from database.income_expense_service import IncomeExpenseService
    income_expense_service = IncomeExpenseService()
    
    total_income = income_expense_service.get_total_income()
    total_expense = income_expense_service.get_total_expense()
    net_profit = income_expense_service.get_net_profit()
    
    income_count = income_expense_service.get_transactions_count('income')
    expense_count = income_expense_service.get_transactions_count('expense')
    
    text = "<b>📈 Financial Analysis</b>\n\n"
    text += "```\n"
    text += f"{'Metric':<25} {'Value':<15}\n"
    text += "-" * 40 + "\n"
    text += f"{'Total Income':<25} {total_income:>15.2f}\n"
    text += f"{'Total Expenses':<25} {total_expense:>15.2f}\n"
    text += f"{'Net Profit':<25} {net_profit:>15.2f}\n"
    text += "-" * 40 + "\n"
    text += f"{'Income Transactions':<25} {income_count:>15}\n"
    text += f"{'Expense Transactions':<25} {expense_count:>15}\n"
    text += "```\n"
    
    if total_income > 0:
        expense_ratio = (total_expense / total_income) * 100
        text += f"\n<b>Expense Ratio:</b> {expense_ratio:.1f}% of income"
    
    if net_profit > 0:
        text += f"\n<b>Status:</b> ✅ Profitable"
    elif net_profit < 0:
        text += f"\n<b>Status:</b> ❌ Loss"
    else:
        text += f"\n<b>Status:</b> ⚖️ Break-even"
    
    keyboard = [
        [InlineKeyboardButton("← Back to Incomes & Expenses", callback_data='income_expense')]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )