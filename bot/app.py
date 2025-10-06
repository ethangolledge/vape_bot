import os
from dotenv import load_dotenv
from telegram.ext import Application
from .handlers import register_handlers
from .data_transfer import DuckDBManager
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VapeBot:
    def __init__(self):
        load_dotenv()
        token = os.getenv("TOKEN")
        
        # initialise app and db
        self.app = Application.builder().token(token).build()
        self.db = DuckDBManager(db_path="vape_tracking.db")
        
        register_handlers(self.app, self.db)

    def run(self):
        """Start the bot and ensure proper cleanup"""
        try:
            logger.info("Starting VapeBot...")
            self.app.run_polling()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            raise
        finally:
            logger.info("Shutting down...")
            self.db.conn.close()