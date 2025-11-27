#!/usr/bin/env python3
"""
Keyboard utilities for creating inline and reply keyboards using python-telegram-bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

class KeyboardTemplates:
    """Predefined keyboard templates"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("Menu", callback_data='menu')],
            [InlineKeyboardButton("About", callback_data='about')],
            [InlineKeyboardButton("Help", callback_data='help')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def submenu() -> InlineKeyboardMarkup:
        """Submenu keyboard"""
        keyboard = [
            [InlineKeyboardButton("Calendar", callback_data='calendar')],
            [InlineKeyboardButton("Orders", callback_data='orders')],
            [InlineKeyboardButton("Employees", callback_data='employees')],
            [InlineKeyboardButton("Tools", callback_data='tools')],
            [InlineKeyboardButton("← Back", callback_data='start')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def orders_menu() -> InlineKeyboardMarkup:
        """Orders menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("➕ Add Order", callback_data='order_add')],
            [InlineKeyboardButton("📋 Show Orders List", callback_data='order_list')],
            [InlineKeyboardButton("← Back to Menu", callback_data='menu')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def employees_menu() -> InlineKeyboardMarkup:
        """Employees menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("➕ Add Employee", callback_data='add_employee')],
            [InlineKeyboardButton("📋 Show Employees List", callback_data='employee_list')],
            [InlineKeyboardButton("💰 Payroll Calculations", callback_data='payroll_list')],
            [InlineKeyboardButton("← Back to Menu", callback_data='menu')]
        ]
        return InlineKeyboardMarkup(keyboard)