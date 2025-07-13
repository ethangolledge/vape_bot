from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from telegram import Update, MessageEntity

@dataclass
class UserProfile:
    """effective_user data"""
    user_id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

    @classmethod
    def from_update(cls, up: Update) -> 'UserProfile':
        user = up.effective_user
        return cls(
            user_id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        )
@dataclass
class ChatContext:
    """effective_chat data"""
    chat_id: int
    chat_type: str
    chat_title: Optional[str] = None
    chat_username: Optional[str] = None
    chat_first_name: Optional[str] = None
    chat_is_forum: Optional[bool] = None

    @classmethod
    def from_update(cls, up: Update) -> 'ChatContext':
        chat = up.effective_chat
        return cls(
            chat_id=chat.id,
            chat_type=chat.type,
            chat_title=getattr(chat, 'title', None),
            chat_username=getattr(chat, 'username', None),
            chat_first_name=getattr(chat, 'first_name', None),
            chat_is_forum=getattr(chat, 'is_forum', None),
        )

@dataclass
class MessageMetadata:
    """message metadata"""
    message_id: Optional[int] = None
    text: Optional[str] = None
    timestamp: Optional[datetime] = None
    entities: Optional[List[MessageEntity]] = None
    is_reply: Optional[bool] = None
    reply_to_message_id: Optional[int] = None

    @classmethod
    def from_update(cls, up: Update) -> 'MessageMetadata':
        message = up.message or (up.callback_query.message if up.callback_query else None)
        return cls(
            message_id=getattr(message, 'message_id', None),
            text=getattr(message, 'text', None),
            timestamp=getattr(message, 'date', None),
            entities=getattr(message, 'entities', None),
            is_reply=hasattr(message, 'reply_to_message') and message.reply_to_message is not None,
            reply_to_message_id=getattr(message.reply_to_message, 'message_id', None)
            if getattr(message, 'reply_to_message', None) else None,
        )

@dataclass
class SetupAnswers:
    """user-provided setup answers"""
    tokes: Optional[str] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    goal: Optional[str] = None

@dataclass
class SessionData:
    """aggregated session object"""
    user: UserProfile
    chat: ChatContext
    message: MessageMetadata
    setup: SetupAnswers = field(default_factory=SetupAnswers)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_update(cls, up: Update) -> 'SessionData':
        return cls(
            user=UserProfile.from_update(up),
            chat=ChatContext.from_update(up),
            message=MessageMetadata.from_update(up),
        )
    
    @property
    def uid(self) -> int:
        """Shortcut for user ID"""
        return self.user.user_id

    @property
    def cid(self) -> int:
        """Shortcut for chat ID"""
        return self.chat.chat_id

    @property
    def uname(self) -> str:
        """Username or first name"""
        return self.user.username if self.user.username else self.user.first_name
    
    def summary(self) -> str:
        return (
            f"Tokes: {self.setup.tokes.capitalize() if self.setup.tokes else self.setup.tokes}\n"
            f"Strength: {self.setup.strength.capitalize() if self.setup.strength else self.setup.strength}\n"
            f"Method: {self.setup.method.capitalize() if self.setup.method else self.setup.method}\n"
            f"Goal: {(self.setup.goal + '%') if self.setup.goal and self.setup.method == 'percent' else self.setup.goal}"
        )