#!/usr/bin/env python3
"""
Setup script for Metrica Telegram Bot
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists("env_template.txt"):
        try:
            with open("env_template.txt", "r") as template:
                content = template.read()
            
            with open(".env", "w") as env_file:
                env_file.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your BOT_TOKEN")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ env_template.txt not found")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Metrica Telegram Bot...")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    print("=" * 40)
    print("✅ Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your BOT_TOKEN")
    print("2. Run: python bot.py")
    print("\n🤖 Your bot will be ready to use!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
