from telegram import (
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove, 
    Update
)
from telegram.ext import (
    Application, 
    CommandHandler,
    ContextTypes, 
    ConversationHandler,
    MessageHandler,
    filters
)
from .models import UserData
from .states import BotStates

class ConversationFlow:
    def __init__(self) -> None:
        """Initialize the bot and set up the relevant classes."""
        self.user_data_store = {}

    async def setup(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Start the conversation and let the user know what to expect."""
        user = up.message.from_user
        user_name = user.first_name
        await up.message.reply_text(
            f"Hi {user_name}. Welcome to the setup! Let's get started with some questions.\n"
            "You can cancel at any time by sending /cancel.\n"
            "First, how many tokes do you take per day?",
            reply_markup=ReplyKeyboardRemove()
        )
        return BotStates.TOKES

    async def ask_stength(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Ask the user how they want to reduce their vaping."""
        user = up.message.from_user
        tokes = up.message.text
        user_data = self.setup_data.setdefault(user.id, UserData(user.id))
        user_data.tokes = tokes

        await up.message.reply_text(
            "Sickna mate.\n"
            "What stength nicotine do you use?\n"
            "For example, 3mg, 6mg, 12mg, etc.",
            reply_markup=ReplyKeyboardRemove()
        )

        return BotStates.STRENGTH

    async def ask_method(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Ask the user how they want to reduce their vaping."""
        reply_keyboard = [["Number"], ["Percent"]]
        user = up.message.from_user
        strength = up.message.text
        user_data = self.setup_data.setdefault(user.id, UserData(user.id))
        user_data.strength = strength

        await up.message.reply_text(
            f"Get ya. We can manage that!\n"
            "How do you want to reduce your vaping?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Choose a method"
            ),
        )

        return BotStates.METHOD

    async def ask_goal(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Ask the user for their weekly reduction goal."""
        user = up.message.from_user
        method = up.message.text
        user_data = self.setup_data.setdefault(user.id, UserData(user.id))
        user_data.method = method


        await up.message.reply_text(
            "Cool beans.\n" 
            "Now, what is your weekly reduction goal? ",
            reply_markup=ReplyKeyboardRemove()
        )

        return BotStates.GOAL

    async def finish_setup(self, up: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Finish the setup and confirm the user's choices."""
        user = up.message.from_user
        goal = up.message.text
        user_data = self.setup_data.setdefault(user.id, UserData(user.id))
        user_data.goal = goal

        await up.message.reply_text(
            user_data.summary() + "\n"
            "Great! Your setup is complete. You can start tracking your vaping reduction now.\n"
            "If you want to change anything, just send /setup again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
        
    async def cancel(self, up:Update, ctx:ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation."""
        user = up.message.from_user
        await up.message.reply_text(
            "Setup cancelled. You can start again with /setup.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def main(self) -> None:
        """Run the bot."""
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("setup", self.setup)],
            states={
                BotStates.TOKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_stength)],
                BotStates.STRENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_method)],
                BotStates.METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_goal)],
                BotStates.GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.finish_setup)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        self.app.add_handler(conv_handler)
        self.app.run_polling()