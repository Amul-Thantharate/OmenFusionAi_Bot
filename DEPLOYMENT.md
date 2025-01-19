# OmenFusionAi_Bot Deployment Guide

## 🚀 Server Deployment

### Prerequisites
1. Ubuntu/Debian server (20.04 LTS or newer recommended)
2. SSH access to the server
3. sudo privileges
4. Git installed

### Step-by-Step Deployment

1. **Connect to your server**
   ```bash
   ssh username@your_server_ip
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/OmenFusionAi_Bot.git
   cd OmenFusionAi_Bot
   ```

3. **Make setup scripts executable**
   ```bash
   chmod +x setup_linux.sh deploy.sh
   ```

4. **Run Linux setup script**
   ```bash
   ./setup_linux.sh
   ```
   This script will:
   - Install system dependencies
   - Set up Python virtual environment
   - Install Python packages
   - Configure ffmpeg and other requirements

5. **Run deployment script**
   ```bash
   ./deploy.sh
   ```

6. **Configure environment variables**
   ```bash
   nano .env
   ```
   Add your bot token and API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   TOGETHER_API_KEY=your_together_api_key
   ```

7. **Restart the service**
   ```bash
   sudo systemctl restart aifusionbot
   ```

### Common Linux Issues

1. **ffmpeg not found**
   ```bash
   sudo apt-get update
   sudo apt-get install -y ffmpeg
   ```

2. **libmagic issues**
   ```bash
   sudo apt-get install -y libmagic1
   ```

3. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER /path/to/OmenFusionAi_Bot
   chmod +x *.sh
   ```

4. **Python version issues**
   ```bash
   python3 --version  # Should be 3.8 or higher
   sudo apt-get install python3.9  # If needed
   ```

### Monitoring & Maintenance

1. **Check service status**
   ```bash
   sudo systemctl status aifusionbot
   ```

2. **View logs**
   ```bash
   sudo journalctl -u aifusionbot -f
   ```

3. **Update the bot**
   ```bash
   cd OmenFusionAi_Bot
   git pull
   source venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart aifusionbot
   ```

### Troubleshooting

1. **If the bot doesn't start:**
   - Check logs: `sudo journalctl -u aifusionbot -f`
   - Verify .env file: `cat .env`
   - Check Python version: `python3 --version`
   - Verify virtual environment: `source venv/bin/activate`

2. **If commands don't work:**
   - Check system dependencies: `./setup_linux.sh`
   - Restart the service: `sudo systemctl restart aifusionbot`
   - Check Telegram bot token
   - Verify internet connection

3. **Memory issues:**
   - Check memory usage: `free -h`
   - Monitor process: `top -u $USER`
   - Check disk space: `df -h`

4. **Permission issues:**
   - Fix ownership: `sudo chown -R $USER:$USER .`
   - Fix permissions: `chmod -R 755 .`
   - Check service user: `sudo systemctl status aifusionbot`

## 📞 Support

If you encounter any issues during deployment:
1. Check the logs
2. Review the troubleshooting guide
3. Open an issue on GitHub
4. Contact the development team

## 🔒 Security Notes

1. Always use HTTPS for production
2. Keep your .env file secure
3. Regularly update dependencies
4. Monitor server resources
5. Back up your data regularly
6. Set proper file permissions
7. Use a firewall (UFW recommended)
