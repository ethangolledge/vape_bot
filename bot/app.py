import os
from dotenv import load_dotenv
from telegram.ext import Application
from .handlers import register_handlers

class vape_bot:
    def __init__(self):
        load_dotenv()
        token = os.getenv("TOKEN")
        self.app = Application.builder().token(token).build()
        register_handlers(self.app)

    def run(self):
        self.app.run_polling()
    