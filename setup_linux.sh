#!/bin/bash

echo "🚀 Setting up AIFusionBot dependencies for Linux..."

# Update package list
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    ffmpeg \
    libmagic1 \
    libpq-dev \
    build-essential \
    portaudio19-dev \
    python3-pyaudio \
    libespeak1

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🌟 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Setup complete! You can now run the bot with: python app.py"
