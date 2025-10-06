from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove, 
    Update
)
from telegram.ext import (
    CommandHandler,
    ContextTypes, 
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from .extractors import TelegramExtractor
from .states import BotStates
from .models import SetupManager
from .data_transfer import DuckDBManager


class ConversationFlow:
    def __init__(self, db: DuckDBManager) -> None:
        """Initialise the conversation flow with session management"""
        self.extractor = TelegramExtractor()
        self.setup = SetupManager()
        self.db = db

    async def start_command(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """simply saying hello and intro"""
        try:
            session = self.extractor.session(up)
            await up.message.reply_text(
                f"Hello {session.uname}\\!\n\n"  # Escape special characters
                "This is an open\\-source messaging service designed to help manage addictive habits, "
                "such as vaping, through tracking, analytics, and accountability\\.\n\n"
                "🔗 GitHub: https://github\\.com/ethangolledge/vape\\_bot\n\n"
                "⚠️ This is a work in progress, but the overall goal is to provide a tech\\-based "
                "solution aimed at addressing addictive habits\\.\n\n"
                "Feel free to reach out with any feedback or suggestions\\!", 
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='MarkdownV2'  # Add parse mode
            )
        except Exception as e:
            print(f"Error in start command: {e}")
            await up.message.reply_text("An error occurred during the start command.")
    
    async def help_command(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """simple command to list available commands"""
        try:
            session = self.extractor.session(up)
            await up.message.reply_text(
                f"Hello {session.uname}! Here are the commands you can use:\n"
                "/setup - Start or modify the setup for tracking and goals\n"
                "/cancel - This is available in conversations.Such as when you are in the setup\n",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as e:
            print(f"Error in help command: {e}")
            await up.message.reply_text("An error occurred during the help command.")

    async def ask_tokes(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """the below is the entry point for the setup conversation"""
        try:
            session = self.extractor.session(up)
            self.setup.get_setup(session.uid)

            await up.message.reply_text(
                f"Hi {session.uname}\\! Let's start setup\\.\n"
                "How many tokes do you have a day\\?\n\n"
                "Send /cancel to stop setup\\.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='MarkdownV2'
            )
            return BotStates.TOKES
        except Exception as e:
            print(f"Error in ask_tokes: {e}")
            return ConversationHandler.END

    async def ask_strength(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            session = self.extractor.session(up)
            user_input = session.message.reply
            if not user_input:
                raise ValueError(
                    f"CID: {session.cid}\n"
                    f"Message ID: {session.message.message_id}\n"
                    f"Timestamp: {session.datetime}\n"
                    f"Err: Missing message text"
                )
            # store tokes into setup, repeat in following functions for other fields
            self.setup.update_setup_field(session.uid, "tokes", user_input)

            await up.message.reply_text(
                "Sickna mate.\n"
                "What strength nicotine are you chomping through? e.g. 3mg, 6mg, 12mg",
                reply_markup=ReplyKeyboardRemove()
            )
            return BotStates.STRENGTH
        except Exception as e:
            print(f"Error in ask_strength: {e}")
            return ConversationHandler.END

    async def ask_method(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            session = self.extractor.session(up)
            user_input = session.message.reply
            
            if not user_input:
                raise ValueError(f"CID: {session.cid}\n"
                    f"Message ID: {session.message.message_id}\n"
                    f"Timestamp: {session.datetime}\n"
                    f"Err: Missing message text"
                )
            
            self.setup.update_setup_field(session.uid, "strength", user_input)

            keyboard = [
                [InlineKeyboardButton("By A Set Number", callback_data="number")],
                [InlineKeyboardButton("Percent", callback_data="percent")]
            ]

            await up.message.reply_text(
                "How do you want to reduce vaping?\nChoose a method:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return BotStates.METHOD
        except Exception as e:
            print(f"Error in ask_method: {e}")
            return ConversationHandler.END

    async def ask_goal(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            session = self.extractor.session(up)
            query_data = session.message.reply
            
            if not query_data:
                raise ValueError(f"CID: {session.cid}\n"
                    f"Message ID: {session.message.message_id}\n"
                    f"Timestamp: {session.datetime}\n"
                    f"Err: Missing callback data"
                )
            
            await up.callback_query.answer()  # still need this to acknowledge the button press
            
            self.setup.update_setup_field(session.uid, "method", query_data)
            
            prompt = "How many tokes do you want to cut down per day?" if query_data == "number" else \
                    "What percentage of your daily tokes do you want to cut down?"

            await up.callback_query.message.reply_text(
                prompt, 
                reply_markup=ReplyKeyboardRemove()
            )
            return BotStates.GOAL
        except Exception as e:
            print(f"Error in ask_goal: {e}")
            return ConversationHandler.END

    async def setup_finish(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            session = self.extractor.session(up)
            user_input = session.message.reply
            
            if not user_input:
                raise ValueError(f"CID: {session.cid}\n"
                    f"Message ID: {session.message.message_id}\n"
                    f"Timestamp: {session.datetime}\n"
                    f"Err: Missing message text"
                )
            
            self.setup.update_setup_field(session.uid, "goal", user_input)
            
            summary = self.setup.summary(session.uid)
            if not summary:
                raise ValueError("Setup data not found, cannot finish setup.")

            #self.db.insert_setup(session.uid, self.setup)

            await up.message.reply_text(
                summary + "\nSetup complete! Send /setup to change anything.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        except Exception as e:
            print(f"Error in setup_finish: {e}")
            return ConversationHandler.END
    
    async def cancel(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            await up.message.reply_text(
                "Setup cancelled. You can start again with /setup.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        except Exception as e:
            print(f"Error in cancel: {e}")
            return ConversationHandler.END

    
    def start(self) -> CommandHandler:
        """Constructs and returns the start command handler."""
        return CommandHandler("start", self.start_command)
    
    def help(self) -> CommandHandler:
        """Constructs and returns the help command handler."""
        return CommandHandler("help", self.help_command)
    
    def setup_build(self) -> ConversationHandler:
        """Constructs and returns the setup conversation handler."""
        return ConversationHandler(
            entry_points=[CommandHandler("setup", self.ask_tokes)],
            states={
                BotStates.TOKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_strength)],
                BotStates.STRENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_method)],
                BotStates.METHOD: [CallbackQueryHandler(self.ask_goal)],
                BotStates.GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.setup_finish)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )