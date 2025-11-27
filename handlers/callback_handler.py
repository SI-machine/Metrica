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
        elif callback_data == 'settings':
            await _handle_settings(update, context)
        elif callback_data == 'employees':
            await _handle_employees(update, context)
        elif callback_data == 'tools':
            await _handle_tools(update, context)
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
    """Handle payroll list callback with pagination"""
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
    
    # Get payroll summary from database
    from database.payroll_service import PayrollService
    payroll_service = PayrollService()
    payroll_summary = payroll_service.get_payroll_summary_by_employee()
    
    # Calculate pagination
    total_entries = len(payroll_summary)
    total_pages = (total_entries + PAYROLL_PER_PAGE - 1) // PAYROLL_PER_PAGE if total_entries > 0 else 1
    
    # Get paginated results
    start_idx = offset
    end_idx = min(offset + PAYROLL_PER_PAGE, total_entries)
    paginated_summary = payroll_summary[start_idx:end_idx]
    
    # Build the message
    text = "<b>💰 Payroll Calculations</b>\n\n"
    
    if not paginated_summary:
        text += "No payroll calculations found."
    else:
        # Format as monospace table
        text += "```\n"
        text += f"{'Employee':<20} {'Orders':<8} {'Total Amount':<15}\n"
        text += "-" * 45 + "\n"
        
        for summary in paginated_summary:
            employee_name = summary['employee_name'][:18] if len(summary['employee_name']) > 18 else summary['employee_name']
            order_count = str(summary['order_count'])
            total_amount = f"{summary['total_amount']:.2f}"
            
            text += f"{employee_name:<20} {order_count:<8} {total_amount:<15}\n"
        
        text += "```\n"
        text += f"\n<b>Page {page + 1} of {total_pages}</b> | <b>Total: {total_entries} employees</b>"
    
    # Build pagination keyboard
    keyboard = []
    
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
async def _handle_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tools callback"""
    query = update.callback_query
    text = "<b>Tools</b>\n\nAdditional tools coming soon!"
    await query.message.reply_text(text, parse_mode='HTML')