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
from telegram.constants import ParseMode # to be used eventually

from .models import SessionData
from .states import BotStates

class ConversationFlow:
    def __init__(self) -> None:
        """Initialise the bot and store user setup sessions."""
        self.user_setup_data = {}

    def _get_session(self, up: Update) -> SessionData:
        """Get or create the session data from the update."""
        uid = up.effective_user.id if up.effective_user else None
        if uid in self.user_setup_data:
            return self.user_setup_data[uid]
        
        session = SessionData.from_update(up)
        if session.uid is None or session.cid is None:
            raise ValueError("Invalid session data: missing user or chat ID.")
        
        self.user_setup_data[session.uid] = session
        return session

    def _update_setup(self, up: Update, field: str, value: str):
        """Helper to update a single setup field and persist it."""
        session = self._get_session(up)
        setattr(session.setup, field, value)
        self.user_setup_data[session.uid] = session

    async def ask_tokes(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            self._get_session(up)  # ensures session is created/stored

            await up.message.reply_text(
                "Hi! Let's start setup.\n"
                "How many tokes do you have a day?",
                reply_markup=ReplyKeyboardRemove()
            )
            return BotStates.TOKES
        except Exception as e:
            print(f"Error in ask_tokes: {e}")

    async def ask_stength(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            if not up.message or not up.message.text:
                raise ValueError("Missing message text.")
            self._update_setup(up, "tokes", up.message.text)

            await up.message.reply_text(
                "Sickna mate.\n"
                "What strength nicotine are you chomping through? e.g. 3mg, 6mg, 12mg",
                reply_markup=ReplyKeyboardRemove()
            )
            return BotStates.STRENGTH
        except Exception as e:
            print(f"Error in ask_stength: {e}")

    async def ask_method(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            if not up.message or not up.message.text:
                raise ValueError("Missing message text.")
            self._update_setup(up, "strength", up.message.text)

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

    async def ask_goal(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            query = up.callback_query
            if not query:
                raise ValueError("Missing callback query.")
            await query.answer()

            self._update_setup(up, "method", query.data)

            prompt = "How many tokes do you want to cut down per day?" if query.data == "number" else \
                     "What percentage of your daily tokes do you want to cut down?"

            await query.message.reply_text(prompt, reply_markup=ReplyKeyboardRemove())
            return BotStates.GOAL
        except Exception as e:
            print(f"Error in ask_goal: {e}")

    async def setup_finish(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            if not up.message or not up.message.text:
                raise ValueError("Missing message text.")
            self._update_setup(up, "goal", up.message.text)

            session = self._get_session(up)
            await up.message.reply_text(
                session.summary() + "\nSetup complete! Send /setup to change anything.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        except Exception as e:
            print(f"Error in setup_finish: {e}")

    async def cancel(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            await up.message.reply_text(
                "Setup cancelled. You can start again with /setup.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        except Exception as e:
            print(f"Error in cancel: {e}")

    def setup_build(self) -> ConversationHandler:
        """Constructs and returns the setup conversation handler."""
        return ConversationHandler(
            entry_points=[CommandHandler("setup", self.ask_tokes)],
            states={
                BotStates.TOKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_stength)],
                BotStates.STRENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_method)],
                BotStates.METHOD: [CallbackQueryHandler(self.ask_goal)],
                BotStates.GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.setup_finish)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )