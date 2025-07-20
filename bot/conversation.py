from telegram import (
    ReplyKeyboardMarkup,
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

from .session_manager import SessionManager
from .extractors import TelegramExtractor
from .states import BotStates

class ConversationFlow:
    def __init__(self) -> None:
        """Initialize the conversation flow with session management"""
        self.session_manager = SessionManager()
        self.extractor = TelegramExtractor()

    async def ask_tokes(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            # Just ensure session exists
            self.session_manager.get_session(up)

            await up.message.reply_text(
                "Hi! Let's start setup.\n"
                "How many tokes do you have a day?",
                reply_markup=ReplyKeyboardRemove()
            )
            return BotStates.TOKES
        except Exception as e:
            print(f"Error in ask_tokes: {e}")
            return ConversationHandler.END

    async def ask_strength(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            session = self.session_manager.get_session(up)
            user_input = self.extractor.extract_current_message_text(up)
            
            if not user_input:
                raise ValueError("Missing message text.")
            
            # Store the user's input
            self.session_manager.update_setup_field(session.uid, "tokes", user_input)

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
            session = self.session_manager.get_session(up)
            user_input = self.extractor.extract_current_message_text(up)
            
            if not user_input:
                raise ValueError("Missing message text.")
            
            self.session_manager.update_setup_field(session.uid, "strength", user_input)

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
            session = self.session_manager.get_session(up)
            query = up.callback_query
            
            if not query:
                raise ValueError("Missing callback query.")
            
            await query.answer()
            
            self.session_manager.update_setup_field(session.uid, "method", query.data)
            
            prompt = "How many tokes do you want to cut down per day?" if query.data == "number" else \
                     "What percentage of your daily tokes do you want to cut down?"

            await query.message.reply_text(prompt, reply_markup=ReplyKeyboardRemove())
            return BotStates.GOAL
        except Exception as e:
            print(f"Error in ask_goal: {e}")
            return ConversationHandler.END

    async def setup_finish(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            session = self.session_manager.get_session(up)
            user_input = self.extractor.extract_current_message_text(up)
            
            if not user_input:
                raise ValueError("Missing message text.")
            
            self.session_manager.update_setup_field(session.uid, "goal", user_input)
            
            # Get the complete setup data for storage/processing
            setup_data = self.session_manager.get_setup_data(session.uid)
            
            # TODO: Here you would store setup_data to your persistent storage
            # await self.storage_service.save_user_setup(session.uid, setup_data)

            await up.message.reply_text(
                setup_data.summary() + "\nSetup complete! Send /setup to change anything.",
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