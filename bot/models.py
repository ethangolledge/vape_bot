from dataclasses import dataclass, field, asdict
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
    tokes: Optional[str] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    goal: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
class SetupManager:
    
    def __init__(self):
        # stuctures the setupdata class into a dictionary for clear management of data
        self.setups: Dict[int, SetupData] = {}
    
    def get_setup(self, user_id: int) -> SetupData:
        """using the dataclass, we assign a user_id to a setup instance"""
        if user_id not in self.setups:
            self.setups[user_id] = SetupData()
        return self.setups[user_id]
    
    def update_setup_field(self, user_id: int, field: str, value: str) -> SetupData:
        """update the field value for a given user_id, within the dictionary"""
        setup = self.get_setup(user_id)
        setattr(setup, field, value)
        return setup 
    
    def setup_dict(self, user_id: int) -> Dict[str, str]:
        """structure the setup data into a dictionary"""
        setup = self.get_setup(user_id)
        return {user_id: asdict(setup)} # this may seem redundant, but for flexibility for either data transfer or display, this is useful
    
    def summary(self, user_id: int) -> str:
        """format for display within telegram"""
        setup = self.setup_dict(user_id)
        user_setup = setup[user_id]
        return (
            f"Tokes: {user_setup['tokes'].capitalize() if user_setup['tokes'] else 'Not set'}\n"
            f"Strength: {user_setup['strength'].capitalize() if user_setup['strength'] else 'Not set'}\n"
            f"Method: {user_setup['method'].capitalize() if user_setup['method'] else 'Not set'}\n"
            f"Goal: {(user_setup['goal'] + '%') if user_setup['goal'] and user_setup['method'] == 'percent' else user_setup['goal'] or 'Not set'}"
        )
