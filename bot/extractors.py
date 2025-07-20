from typing import Optional
from telegram import Update
from .models import UserProfile, ChatContext, MessageMetadata, SessionData

class TelegramExtractor:
    """Extracts data from Telegram Updates"""
    
    @staticmethod
    def extract_user(update: Update) -> UserProfile:
        user = update.effective_user
        return UserProfile(
            user_id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        )
    
    @staticmethod
    def extract_chat(update: Update) -> ChatContext:
        chat = update.effective_chat
        return ChatContext(
            chat_id=chat.id,
            chat_type=chat.type,
            chat_title=getattr(chat, 'title', None),
            chat_username=getattr(chat, 'username', None),
            chat_first_name=getattr(chat, 'first_name', None),
            chat_is_forum=getattr(chat, 'is_forum', None),
        )
    
    @staticmethod
    def extract_message(update: Update) -> MessageMetadata:
        message = update.message or (update.callback_query.message if update.callback_query else None)
        return MessageMetadata(
            message_id=getattr(message, 'message_id', None),
            reply=getattr(message, 'text', None),
            timestamp=getattr(message, 'date', None),
            entities=getattr(message, 'entities', None),
            is_reply=hasattr(message, 'reply_to_message') and message.reply_to_message is not None,
            reply_to_message_id=getattr(message.reply_to_message, 'message_id', None)
            if getattr(message, 'reply_to_message', None) else None,
        )
    
    @staticmethod
    def extract_current_message_text(update: Update) -> Optional[str]:
        """Get current message text without storing it"""
        if update.callback_query:
            return update.callback_query.data
        elif update.message:
            return update.message.text
        return None
    
    @staticmethod
    def create_session(update: Update) -> SessionData:
        """Create complete session from update"""
        return SessionData(
            user=TelegramExtractor.extract_user(update),
            chat=TelegramExtractor.extract_chat(update),
            message=TelegramExtractor.extract_message(update),
        )