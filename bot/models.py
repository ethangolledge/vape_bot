from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from telegram import Update, MessageEntity

@dataclass
class UserProfile:
    """Pure data representation of a user"""
    user_id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

@dataclass
class ChatContext:
    """Pure data representation of chat context"""
    chat_id: int
    chat_type: str
    chat_title: Optional[str] = None
    chat_username: Optional[str] = None
    chat_first_name: Optional[str] = None
    chat_is_forum: Optional[bool] = None

@dataclass
class MessageMetadata:
    """Pure data representation of message metadata"""
    message_id: Optional[int] = None
    reply: Optional[str] = None
    timestamp: Optional[datetime] = None
    entities: Optional[List[MessageEntity]] = None
    is_reply: Optional[bool] = None
    reply_to_message_id: Optional[int] = None

@dataclass
class SetupAnswers:
    """User setup configuration data"""
    tokes: Optional[str] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    goal: Optional[str] = None
    
    def summary(self) -> str:
        """Format setup data for display"""
        return (
            f"Tokes: {self.tokes.capitalize() if self.tokes else 'Not set'}\n"
            f"Strength: {self.strength.capitalize() if self.strength else 'Not set'}\n"
            f"Method: {self.method.capitalize() if self.method else 'Not set'}\n"
            f"Goal: {(self.goal + '%') if self.goal and self.method == 'percent' else self.goal or 'Not set'}"
        )

@dataclass
class SessionData:
    """Complete session data"""
    user: UserProfile
    chat: ChatContext
    message: MessageMetadata
    setup: SetupAnswers = field(default_factory=SetupAnswers)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def uid(self) -> int:
        return self.user.user_id
    
    @property
    def cid(self) -> int:
        return self.chat.chat_id
    
    @property
    def uname(self) -> str:
        return self.user.username if self.user.username else self.user.first_name