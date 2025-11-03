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
            [InlineKeyboardButton("Календарь", callback_data='calendar')],
            [InlineKeyboardButton("Settings", callback_data='settings')],
            [InlineKeyboardButton("Reports", callback_data='reports')],
            [InlineKeyboardButton("Tools", callback_data='tools')],
            [InlineKeyboardButton("← Back", callback_data='start')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("Notifications", callback_data='settings_notifications')],
            [InlineKeyboardButton("Language", callback_data='settings_language')],
            [InlineKeyboardButton("Privacy", callback_data='settings_privacy')],
            [InlineKeyboardButton("← Back to Menu", callback_data='menu')]
        ]
        return InlineKeyboardMarkup(keyboard)