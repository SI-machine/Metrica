# Metrica Bot

A modular Telegram bot built with Python using the python-telegram-bot framework, featuring a clean architecture and easy extensibility.

## Features

- **python-telegram-bot Framework**: Built on the most popular Python Telegram bot framework
- **Async/Await**: Modern asynchronous code for better performance
- **Modular Architecture**: Clean separation of concerns with dedicated handlers
- **Command Processing**: Handle `/start`, `/help`, `/about` commands
- **Interactive Keyboards**: Inline keyboards for user interaction
- **Media Support**: Handle photos, documents, videos, and other media
- **Proper Logging**: Comprehensive logging system with file and console output
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Robust error handling and automatic retries
- **Easy to Extend**: Simple handler registration system

## Project Structure

```
Metrica/
├── bot.py                     # Main bot file (python-telegram-bot)
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── handlers/                  # Message handlers
│   ├── __init__.py
│   ├── command_handler.py     # Command functions (/start, /help, /about)
│   ├── callback_handler.py    # Button callback functions
│   ├── message_handler.py     # Text message functions
│   └── media_handler.py       # Media message functions
└── utils/                     # Utility modules
    ├── __init__.py
    ├── keyboards.py           # Keyboard builders
    └── logging_config.py      # Logging configuration
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Follow the instructions to get your bot token

### 3. Configure Environment

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_bot_token_here
DEBUG=false
LOG_LEVEL=INFO
```

### 4. Run the Bot

```bash
python bot.py
```

## Architecture

### python-telegram-bot Framework

The bot is built on the **python-telegram-bot** framework which provides:

- **Automatic Handler Routing**: Framework automatically routes updates to the right handler
- **Built-in Error Handling**: Automatic retries and error recovery
- **Async/Await Support**: Modern asynchronous code for better performance
- **Type Safety**: Full type hints support
- **Easy Testing**: Simple to write unit tests

### Handler Functions

Each type of message is processed by dedicated async functions:

- **Command Handlers**: `start_command()`, `help_command()`, `about_command()`
- **Callback Handler**: `button_callback()` handles inline keyboard button clicks
- **Message Handler**: `handle_text_message()` processes regular text
- **Media Handlers**: `handle_photo()`, `handle_document()`, `handle_video()`, etc.

### Configuration Management

The `Config` class handles all configuration:
- Environment variable loading
- `.env` file support
- Configuration validation
- Default values

### Logging

Comprehensive logging system:
- Console and file output
- Configurable log levels
- Debug mode with detailed information
- Automatic error logging

## Adding New Features

### 1. New Command

**Example: Add a `/stats` command**

```python
# In handlers/command_handler.py
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command"""
    text = "<b>Bot Statistics</b>\n\nUsers: 100\nMessages: 1000"
    await update.message.reply_text(text, parse_mode='HTML')

# In bot.py
application.add_handler(CommandHandler("stats", stats_command))
```

### 2. New Callback Action

**Example: Add a new button action**

```python
# In handlers/callback_handler.py
async def _handle_new_feature(query) -> None:
    """Handle new feature callback"""
    text = "<b>New Feature</b>\n\nThis is a new feature!"
    await query.message.reply_text(text, parse_mode='HTML')

# Add to button_callback function
elif callback_data == 'new_feature':
    await _handle_new_feature(query)
```

### 3. New Media Type

**Example: Handle location messages**

```python
# In handlers/media_handler.py
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle location messages"""
    location = update.message.location
    text = f"Thanks for sharing your location!\nLat: {location.latitude}\nLon: {location.longitude}"
    await update.message.reply_text(text)

# In bot.py
application.add_handler(MessageHandler(filters.LOCATION, handle_location))
```

### 4. Add Conversation Flow

**Example: Multi-step registration**

```python
from telegram.ext import ConversationHandler

# Define states
NAME, AGE = range(2)

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("What's your name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("How old are you?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text(f"Registration complete! Welcome {context.user_data['name']}!")
    return ConversationHandler.END

# In bot.py
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('register', start_registration)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
    },
    fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
)
application.add_handler(conv_handler)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token (required) | - |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `WEBHOOK_URL` | Webhook URL (for production) | - |
| `WEBHOOK_PORT` | Webhook port | `8443` |

## Logging

Logs are written to both console and `bot.log` file. Log levels:

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about bot operation
- `WARNING`: Warning messages
- `ERROR`: Error messages

## Error Handling

The bot includes comprehensive error handling:

- API request failures are logged and handled gracefully
- Handler errors don't crash the bot
- Configuration validation prevents startup with invalid settings
- Network timeouts are handled appropriately

## Development

### Running in Debug Mode

Set `DEBUG=true` in your `.env` file for detailed logging and error information.

### Adding Dependencies

Add new dependencies to `requirements.txt` and install with:

```bash
pip install -r requirements.txt
```

### Code Style

The code follows Python PEP 8 guidelines and includes:
- Type hints for better code documentation
- Docstrings for all public methods
- Clear separation of concerns
- Consistent error handling

## Production Deployment

For production deployment:

1. Use environment variables instead of `.env` file
2. Set up proper logging rotation
3. Consider using a process manager like systemd
4. Implement webhook mode for better performance
5. Add monitoring and health checks

## License

This project is part of the Metrica project.