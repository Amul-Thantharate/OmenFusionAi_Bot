import requests
import time
import logging
import psutil
import os
from datetime import datetime
from telegram import Bot
import asyncio
from typing import Optional, List, Dict
import json

class SystemStats:
    @staticmethod
    def get_cpu_usage() -> float:
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        memory = psutil.virtual_memory()
        return {
            "total": round(memory.total / (1024.0 ** 3), 2),  # GB
            "used": round(memory.used / (1024.0 ** 3), 2),    # GB
            "percent": memory.percent
        }

    @staticmethod
    def get_disk_usage() -> Dict[str, float]:
        disk = psutil.disk_usage('/')
        return {
            "total": round(disk.total / (1024.0 ** 3), 2),    # GB
            "used": round(disk.used / (1024.0 ** 3), 2),      # GB
            "percent": disk.percent
        }

class BotMonitor:
    def __init__(
        self,
        bot_token: str,
        admin_chat_ids: List[str],
        check_interval: int = 300,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        disk_threshold: float = 80.0
    ):
        self.bot_token = bot_token
        self.admin_chat_ids = admin_chat_ids
        self.check_interval = check_interval
        self.bot = Bot(token=bot_token)
        self.last_status = True
        self.last_alert_time = {}  # To prevent alert spam
        self.alert_cooldown = 1800  # 30 minutes
        self.system_stats = SystemStats()
        
        # Thresholds for alerts
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = 'bot_monitor.log'
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    async def check_bot_status(self) -> bool:
        """Check if the bot is responsive"""
        try:
            await self.bot.get_me()
            self.logger.info("Bot check: OK")
            return True
        except Exception as e:
            self.logger.error(f"Bot check failed: {str(e)}")
            return False

    async def check_server_status(self, server_url: str) -> bool:
        """Check if the server is responsive"""
        try:
            response = requests.get(server_url, timeout=10)
            is_ok = response.status_code == 200
            self.logger.info(f"Server check: {'OK' if is_ok else 'FAILED'}")
            return is_ok
        except Exception as e:
            self.logger.error(f"Server check failed: {str(e)}")
            return False

    async def check_system_resources(self) -> Dict[str, bool]:
        """Check system resource usage"""
        try:
            cpu_usage = self.system_stats.get_cpu_usage()
            memory_usage = self.system_stats.get_memory_usage()
            disk_usage = self.system_stats.get_disk_usage()

            return {
                "cpu": cpu_usage < self.cpu_threshold,
                "memory": memory_usage["percent"] < self.memory_threshold,
                "disk": disk_usage["percent"] < self.disk_threshold,
                "stats": {
                    "cpu": cpu_usage,
                    "memory": memory_usage,
                    "disk": disk_usage
                }
            }
        except Exception as e:
            self.logger.error(f"Resource check failed: {str(e)}")
            return {"cpu": True, "memory": True, "disk": True, "stats": {}}

    def can_send_alert(self, alert_type: str) -> bool:
        """Check if enough time has passed since the last alert"""
        current_time = time.time()
        if alert_type not in self.last_alert_time:
            return True
        
        time_since_last = current_time - self.last_alert_time[alert_type]
        return time_since_last >= self.alert_cooldown

    async def send_alert(self, message: str, alert_type: str = "general"):
        """Send alert to admin users with rate limiting"""
        if not self.can_send_alert(alert_type):
            self.logger.info(f"Skipping alert ({alert_type}): Too soon since last alert")
            return

        self.last_alert_time[alert_type] = time.time()
        
        for chat_id in self.admin_chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"🚨 ALERT: {message}\n\n"
                         f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                self.logger.info(f"Alert sent to {chat_id}: {message}")
            except Exception as e:
                self.logger.error(f"Failed to send alert to {chat_id}: {str(e)}")

    def format_system_stats(self, stats: Dict) -> str:
        """Format system statistics for messages"""
        return (
            f"System Statistics:\n"
            f"CPU Usage: {stats['cpu']}%\n"
            f"Memory: {stats['memory']['used']}/{stats['memory']['total']} GB "
            f"({stats['memory']['percent']}%)\n"
            f"Disk: {stats['disk']['used']}/{stats['disk']['total']} GB "
            f"({stats['disk']['percent']}%)"
        )

    async def monitor_loop(self, server_url: Optional[str] = None):
        """Main monitoring loop"""
        self.logger.info("Starting monitoring service...")
        await self.send_alert("🟢 Monitoring service started", "startup")

        while True:
            try:
                # Check bot status
                bot_status = await self.check_bot_status()
                
                # Check server status if URL provided
                server_status = True
                if server_url:
                    server_status = await self.check_server_status(server_url)

                # Check system resources
                resource_status = await self.check_system_resources()
                
                # Prepare status message
                alerts = []
                if not bot_status:
                    alerts.append("❌ Bot is not responding")
                if not server_status:
                    alerts.append("❌ Server is not responding")
                if not resource_status["cpu"]:
                    alerts.append(f"⚠️ High CPU usage: {resource_status['stats']['cpu']}%")
                if not resource_status["memory"]:
                    alerts.append(f"⚠️ High Memory usage: {resource_status['stats']['memory']['percent']}%")
                if not resource_status["disk"]:
                    alerts.append(f"⚠️ High Disk usage: {resource_status['stats']['disk']['percent']}%")

                # Send alerts if needed
                if alerts:
                    if self.last_status:  # Only send alert if status changed from up to down
                        alert_message = "System Status Update:\n" + "\n".join(alerts)
                        alert_message += f"\n\n{self.format_system_stats(resource_status['stats'])}"
                        await self.send_alert(alert_message, "system_issue")
                        self.last_status = False
                elif not self.last_status:  # System recovered
                    recovery_message = (
                        "✅ Systems are back online and functioning normally!\n\n"
                        f"{self.format_system_stats(resource_status['stats'])}"
                    )
                    await self.send_alert(recovery_message, "system_recovery")
                    self.last_status = True

                # Log current status
                self.logger.info(
                    f"Status check completed - Bot: {'OK' if bot_status else 'FAIL'}, "
                    f"Server: {'OK' if server_status else 'FAIL'}"
                )

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")

            await asyncio.sleep(self.check_interval)

    def start_monitoring(self, server_url: Optional[str] = None):
        """Start the monitoring service"""
        try:
            asyncio.run(self.monitor_loop(server_url))
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            raise

    def get_current_status(self) -> Dict:
        """Get current system status for manual checks"""
        try:
            stats = {
                "cpu": self.system_stats.get_cpu_usage(),
                "memory": self.system_stats.get_memory_usage(),
                "disk": self.system_stats.get_disk_usage(),
                "timestamp": datetime.now().isoformat()
            }
            return {
                "status": "healthy" if self.last_status else "issues_detected",
                "stats": stats
            }
        except Exception as e:
            self.logger.error(f"Failed to get current status: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
