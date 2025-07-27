from typing import Optional
from telegram import Update
from .models import UserProfile, ChatContext, MessageMetadata, SessionData

class TelegramExtractor:
    """Extracts data from Telegram Updates"""
    
    @staticmethod
    def extract_user(up: Update) -> UserProfile:
        user = up.effective_user
        return UserProfile(
            user_id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        )
    
    @staticmethod
    def extract_chat(up: Update) -> ChatContext:
        chat = up.effective_chat
        return ChatContext(
            chat_id=chat.id,
            chat_type=chat.type,
            chat_title=getattr(chat, 'title', None),
            chat_username=getattr(chat, 'username', None),
            chat_first_name=getattr(chat, 'first_name', None),
            chat_is_forum=getattr(chat, 'is_forum', None),
        )
    
    @staticmethod
    def extract_message(up: Update) -> MessageMetadata:
        message = up.message or (up.callback_query.message if up.callback_query else None)
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
    def extract_current_message_text(up: Update) -> Optional[str]:
        """Get current message text without storing it
        Also simplifies callback query data extraction"""
        if up.callback_query:
            return up.callback_query.data
        elif up.message:
            return up.message.text
        return None
    
    @staticmethod
    def session(up: Update) -> SessionData:
        """Create complete session from update (Telegram data only)"""
        return SessionData(
            user=TelegramExtractor.extract_user(up),
            chat=TelegramExtractor.extract_chat(up),
            message=TelegramExtractor.extract_message(up),
        )
    