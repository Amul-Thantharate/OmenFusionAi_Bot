import mysql.connector
import json
from datetime import datetime
from dotenv import load_dotenv
import os

class DatabaseHelper:
    def __init__(self):
        load_dotenv()
        self.connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'omen'),
            password=os.getenv('MYSQL_PASSWORD', 'root@123'),
            database=os.getenv('MYSQL_DATABASE', 'telegram_bot')
        )
        self.cursor = self.connection.cursor()
        self.setup_database()

    def setup_database(self):
        """Create necessary tables if they don't exist."""
        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                is_subscribed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Chat history table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                message TEXT,
                response TEXT,
                model VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Image generations table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_generations (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                prompt TEXT,
                enhanced_prompt TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Image captions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_captions (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                image_url TEXT,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Text enhancements table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS text_enhancements (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                original_text TEXT,
                enhanced_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Image descriptions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_descriptions (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                image_url TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Video analysis table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_analysis (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                video_url TEXT,
                analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        self.connection.commit()

    def add_or_update_user(self, user_id, username=None, first_name=None, last_name=None):
        """Add or update a user in the database."""
        sql = """
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            username = VALUES(username),
            first_name = VALUES(first_name),
            last_name = VALUES(last_name)
        """
        self.cursor.execute(sql, (user_id, username, first_name, last_name))
        self.connection.commit()

    def store_chat(self, user_id, message, response, model):
        """Store a chat interaction."""
        sql = """
            INSERT INTO chat_history (user_id, message, response, model)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, message, response, model))
        self.connection.commit()

    def store_image_generation(self, user_id, prompt, enhanced_prompt, image_url):
        """Store an image generation."""
        sql = """
            INSERT INTO image_generations (user_id, prompt, enhanced_prompt, image_url)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, prompt, enhanced_prompt, image_url))
        self.connection.commit()

    def store_image_caption(self, user_id, image_url, caption):
        """Store an image caption."""
        sql = """
            INSERT INTO image_captions (user_id, image_url, caption)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, image_url, caption))
        self.connection.commit()

    def store_text_enhancement(self, user_id, original_text, enhanced_text):
        """Store a text enhancement."""
        sql = """
            INSERT INTO text_enhancements (user_id, original_text, enhanced_text)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, original_text, enhanced_text))
        self.connection.commit()

    def store_image_description(self, user_id, image_url, description):
        """Store an image description."""
        sql = """
            INSERT INTO image_descriptions (user_id, image_url, description)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, image_url, description))
        self.connection.commit()

    def store_video_analysis(self, user_id, video_url, analysis):
        """Store a video analysis."""
        sql = """
            INSERT INTO video_analysis (user_id, video_url, analysis)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, video_url, analysis))
        self.connection.commit()

    def update_subscription(self, user_id, is_subscribed):
        """Update user's subscription status."""
        sql = """
            UPDATE users
            SET is_subscribed = %s
            WHERE user_id = %s
        """
        self.cursor.execute(sql, (is_subscribed, user_id))
        self.connection.commit()

    def get_user_history(self, user_id):
        """Get all history for a user."""
        result = {
            'chat_history': [],
            'image_generations': [],
            'image_captions': [],
            'text_enhancements': [],
            'image_descriptions': [],
            'video_analysis': []
        }

        # Get chat history
        self.cursor.execute(
            "SELECT message, response, model, created_at FROM chat_history WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        result['chat_history'] = [dict(zip(['message', 'response', 'model', 'created_at'], row)) for row in self.cursor.fetchall()]

        # Get image generations
        self.cursor.execute(
            "SELECT prompt, enhanced_prompt, image_url, created_at FROM image_generations WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        result['image_generations'] = [dict(zip(['prompt', 'enhanced_prompt', 'image_url', 'created_at'], row)) for row in self.cursor.fetchall()]

        # Add similar queries for other tables...

        return result

    def close(self):
        """Close database connection."""
        self.cursor.close()
        self.connection.close() 