import os
from dotenv import load_dotenv
from telegram.ext import Application
from .handlers import register_handlers
from data.database import DuckDBManager
from logger import setup_logger

class VapeBot:
    def __init__(self):
        load_dotenv()
        token = os.getenv("TOKEN")
        
        # logging
        self.logger = setup_logger('bot_development')
        # initialise app
        self.app = Application.builder().token(token).build()
        
        register_handlers(self.app)

    def run(self):
        try:
            self.logger.info("Starting VapeBot...")
            self.app.run_polling()
        except Exception as e:
            self.logger.error(f"Bot error: {e}")
            raise
        finally:
            self.logger.info("Shutting down...")
            self.db.close()