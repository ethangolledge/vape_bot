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
        """Initialise the bot and set up the relevant classes."""
        self.user_setup_data = {}
    def _get_session(self, up: Update) -> SessionData:
        """Get the session data from the update."""
        return SessionData.from_update(up)

    """The below functions are used to handle the setup process"""
    """Eventually, when we have a database, this will be used to store the user data.
       I'd like to add functionality to check whether they have set up and whether they want to overwrite their data."""
    
    async def ask_tokes(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """This is the entry function to setup.
           Provides a breif explaination of the setup process and also how many tokes the user has a day."""
        """Reckon we also need to handle whether the user is in a group or not, a bot etc. Few things to consider."""
        try:
            user_data = SessionData.from_update(up)

            if user_data.user.uid is None or user_data.cid is None:
                raise ValueError("User ID or Chat ID not found in the update.")
            # Initialise the user id key within the session to temp store data
            self.user_session_data[user_data.user.uid] = user_data

            await up.message.reply_text(
                f"Hi {user_data.uname}, welcome to the setup!\n"
                "Let's get started with some questions.\n"
                "You can cancel at any time by sending /cancel.\n\n"
                "Please tell me how many tokeskis you have a day.\n"
                "Don't be telling no porkies!\n"
                "This number will be used to calculate your reduction plan.\n",
                reply_markup=ReplyKeyboardRemove()
            )
            return BotStates.TOKES
        except Exception as e:
            print(f"Error in ask_tokes: {e}")

    async def ask_stength(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Ask the user the strengh of nicotine they use."""
        try:
            user_data = SessionData.from_update(up)
            if user_data is None:
                raise ValueError("User data not found in the update.")
            
            # Store the response in the user session
            # We are gonna have to apply some sort of validation/parsing here
            user_data.tokes = up.message.text

            await up.message.reply_text(
                "Sickna mate.\n"
                "Now, what stength nicotine are you chomping through?\n"
                "For example, 3mg, 6mg, 12mg, etc.\n\n",
                reply_markup=ReplyKeyboardRemove()
            )

            return BotStates.STRENGTH
        except Exception as e:
            print(f"Error in ask_strength: {e}")

    async def ask_method(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Ask the user how they want to reduce their vaping."""
        user_data = self.user_session_data.setdefault(self._uid(up), UserData(user_id=self._uid(up)))
        # Store the data prompted by the previous function, this follows the same pattern for latter functions
        user_data.strength = up.message.text

        keyboard = [
            [InlineKeyboardButton("By A Set Number", callback_data="number")],
            [InlineKeyboardButton("Percent", callback_data="percent")]
        ]

        await up.message.reply_text(
            f"Alright, let's figure out how you want to reduce your vaping.\n\n"
            "You can choose to:\n"
            "• Reduce by a specific number of tokes each day\n"
            "• Reduce by a percentage of your daily tokes\n\n"
            "Which method works better for you?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return BotStates.METHOD

    async def ask_goal(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Ask the user for their weekly reduction goal."""
        query = up.callback_query
        await query.answer()

        user_data = self.user_session_data.setdefault(self._uid(up), UserData(user_id=self._uid(up)))
        user_data.method = query.data

        if user_data.method == "number":
            await query.message.reply_text(
                "Cool beans.\n"
                "Now, how many tokes do you want to cut down per day?",
                reply_markup=ReplyKeyboardRemove()
            )
        elif user_data.method == "percent":
            await query.message.reply_text(
                "Cool beans.\n"
                "Now, what percentage of your daily tokes do you want to cut down?",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            raise ValueError("Invalid method selected.")

        return BotStates.GOAL

    async def setup_finish(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Finish the setup and confirm the user's choices."""
        user_data = self.user_session_data.setdefault(self._uid(up), UserData(user_id=self._uid(up)))
        user_data.goal = up.message.text

        await up.message.reply_text(
            user_data.summary() + "\n"
            "Great! Your setup is complete.\n\n"
            "We've saved your preferences:\n"
            "You can start tracking your tokes.\n"
            "If you want to change anything, just send /setup again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
        
    async def cancel(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation."""
        await up.message.reply_text(
            "Setup cancelled. You can start again with /setup.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def setup_build(self) -> None:
        """Run the bot."""
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