from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
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
class SessionData:
    """Telegram-specific session data only"""
    user: UserProfile
    chat: ChatContext
    message: MessageMetadata
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
    
@dataclass
class SetupData:
    """Abstract setup data - user responses only, independent of Telegram"""
    tokes: Optional[str] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    goal: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_complete(self) -> bool:
        """Check if all required setup fields are filled"""
        return all([self.tokes, self.strength, self.method, self.goal])
    
    def summary(self) -> str:
        """Format setup data for display"""
        return (
            f"Tokes: {self.tokes.capitalize() if self.tokes else 'Not set'}\n"
            f"Strength: {self.strength.capitalize() if self.strength else 'Not set'}\n"
            f"Method: {self.method.capitalize() if self.method else 'Not set'}\n"
            f"Goal: {(self.goal + '%') if self.goal and self.method == 'percent' else self.goal or 'Not set'}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            'tokes': self.tokes,
            'strength': self.strength,
            'method': self.method,
            'goal': self.goal,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SetupData':
        """Create from dictionary (for loading from storage)"""
        return cls(
            tokes=data.get('tokes'),
            strength=data.get('strength'),
            method=data.get('method'),
            goal=data.get('goal'),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )