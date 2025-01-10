#!/bin/bash

echo "🚀 Starting OmenFusionAi_Bot deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv

# Create virtual environment
echo "🌟 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
echo "🔐 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️ Please edit .env file with your actual values"
fi

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/aifusionbot.service << EOF
[Unit]
Description=OmenFusionAi_Bot Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:$PATH
ExecStart=$(pwd)/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the service
echo "🎯 Starting OmenFusionAi_Bot service..."
sudo systemctl daemon-reload
sudo systemctl enable aifusionbot
sudo systemctl start aifusionbot

echo "✅ Deployment complete! Check status with: sudo systemctl status aifusionbot"
