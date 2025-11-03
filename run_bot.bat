@echo off
echo Starting Metrica Telegram Bot...
echo.

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found!
    echo Please run setup.py first or create .env file manually.
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import telegram" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Run the bot
python bot.py

pause
