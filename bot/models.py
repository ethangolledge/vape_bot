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
class SetupData:
    """Independent user setup configuration data"""
    tokes: Optional[str] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    goal: Optional[str] = None
    
    def is_complete(self) -> bool:
        """Check if all required setup fields are completed"""
        return all([self.tokes, self.strength, self.method, self.goal])
    
    def is_valid(self) -> bool:
        """Validate setup data consistency"""
        if not self.is_complete():
            return False
        
        # Validate method is one of expected values
        if self.method not in ['number', 'percent']:
            return False
            
        # Add other validation as needed
        return True
    
    def summary(self) -> str:
        """Format setup data for display"""
        return (
            f"Tokes: {self.tokes.capitalize() if self.tokes else 'Not set'}\n"
            f"Strength: {self.strength.capitalize() if self.strength else 'Not set'}\n"
            f"Method: {self.method.capitalize() if self.method else 'Not set'}\n"
            f"Goal: {(self.goal + '%') if self.goal and self.method == 'percent' else self.goal or 'Not set'}"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'tokes': self.tokes,
            'strength': self.strength,
            'method': self.method,
            'goal': self.goal
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SetupData':
        """Create instance from dictionary"""
        return cls(
            tokes=data.get('tokes'),
            strength=data.get('strength'),
            method=data.get('method'),
            goal=data.get('goal')
        )

# Backward compatibility alias
SetupAnswers = SetupData

@dataclass
class SessionData:
    """Telegram session metadata only"""
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