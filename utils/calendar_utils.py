#!/usr/bin/env python3
"""
Calendar utilities for creating and managing calendar views using python-telegram-bot-calendar
"""

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime

def create_calendar(min_date: datetime = None, max_date: datetime = None) -> tuple[str, object]:
    """
    Create a calendar view with the current month
    
    Args:
        min_date: Optional minimum selectable date. Defaults to None (no minimum).
        max_date: Optional maximum selectable date. Defaults to None (no maximum).
    
    Returns:
        Tuple of (calendar markup object, current step)
    """
    calendar = DetailedTelegramCalendar(min_date=min_date, max_date=max_date)
    calendar_markup, step = calendar.build()
    
    return calendar_markup, step

