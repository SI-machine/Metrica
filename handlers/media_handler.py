#!/usr/bin/env python3
"""
Media handler for processing photos, documents, and other media using python-telegram-bot
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging
from auth.decorators import require_auth

logger = logging.getLogger(__name__)

@require_auth
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent a photo")
    
    try:
        text = "Nice photo! Photo processing features coming soon!"
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await update.message.reply_text("Sorry, something went wrong processing your photo.")

@require_auth
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document messages"""
    user_id = update.effective_user.id
    filename = update.message.document.file_name
    logger.info(f"User {user_id} sent document: {filename}")
    
    try:
        text = f"I received a document: {filename}\n\nDocument processing coming soon!"
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("Sorry, something went wrong processing your document.")

@require_auth
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle video messages"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent a video")
    
    try:
        text = "Great video! Video processing features coming soon!"
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error handling video: {e}")
        await update.message.reply_text("Sorry, something went wrong processing your video.")

@require_auth
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio messages"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent audio")
    
    try:
        text = "I received an audio file! Audio processing coming soon!"
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error handling audio: {e}")
        await update.message.reply_text("Sorry, something went wrong processing your audio.")

@require_auth
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent a voice message")
    
    try:
        text = "Voice message received! Voice processing coming soon!"
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error handling voice: {e}")
        await update.message.reply_text("Sorry, something went wrong processing your voice message.")

@require_auth
async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle sticker messages"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent a sticker")
    
    try:
        text = "Nice sticker! 😊"
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error handling sticker: {e}")
        await update.message.reply_text("Sorry, something went wrong.")