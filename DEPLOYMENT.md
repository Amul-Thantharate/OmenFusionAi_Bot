# AIFusionBot Deployment Guide

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
   git clone https://github.com/yourusername/AIFusionBot.git
   cd AIFusionBot
   ```

3. **Make deploy script executable**
   ```bash
   chmod +x deploy.sh
   ```

4. **Run deployment script**
   ```bash
   ./deploy.sh
   ```

5. **Configure environment variables**
   ```bash
   nano .env
   ```
   Add your bot token and API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   TOGETHER_API_KEY=your_together_api_key
   ```

6. **Restart the service**
   ```bash
   sudo systemctl restart aifusionbot
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
   cd AIFusionBot
   git pull
   sudo systemctl restart aifusionbot
   ```

### Troubleshooting

1. **If the bot doesn't start:**
   - Check logs: `sudo journalctl -u aifusionbot -f`
   - Verify .env file: `cat .env`
   - Check Python version: `python3 --version`

2. **If commands don't work:**
   - Restart the service: `sudo systemctl restart aifusionbot`
   - Check Telegram bot token
   - Verify internet connection

3. **Memory issues:**
   - Check memory usage: `free -h`
   - Monitor process: `top -u $USER`

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
