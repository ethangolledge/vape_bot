from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from telegram import Update, MessageEntity
import logging

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
    tokes: Optional[int] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    reduce_amount: Optional[int] = None
    reduce_percent: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class SetupManager:
    def __init__(self):
        self.setups: Dict[int, SetupData] = {}
        self.goal_field_map = {
            "number": "reduce_amount", 
            "percent": "reduce_percent"
            } # mapping for later calculation
    
    def __calc_metric__(self, numerator: float, denominator: float, to_amount: bool = False) -> Optional[float]:
        """dunder method to calculate either percentage or absolute amount"""
        if denominator == 0:
            return None
        return round((numerator / 100 * denominator) if to_amount else (numerator / denominator * 100), 2)

    def enforce_type(self, field: str, value) -> SetupData:
        """enforce the datatype specified within the dataclass"""
        field_types = SetupData.__annotations__
        expected_type = field_types.get(field)

        if expected_type is None:
            raise ValueError(f"Field '{field}' does not exist in SetupData.")
        
        try:
            if expected_type in (Optional[int], int):
                return int(value) if value is not None else None
            elif expected_type in (Optional[float], float):
                if isinstance(value, str) and value.endswith("%"):
                    return float(value.strip("%"))
                return float(value) if value is not None else None
            elif expected_type in (Optional[str], str):
                return str(value) if value is not None else None
            elif expected_type in (Optional[datetime], datetime):
                if isinstance(value, datetime):
                    return value
                return datetime.fromisoformat(value)
            else:
                return value  # fallback, may need to come back to this
        except Exception as e:
            raise ValueError(f"Invalid value for {field}. Expected {expected_type}, got {type(value)}")

    def get_setup(self, user_id: int) -> SetupData:
        if user_id not in self.setups:
            self.setups[user_id] = SetupData()
        return self.setups[user_id]
    
    def update_setup_field(self, user_id: int, field: str, value) -> SetupData:
        """Update a user’s setup field with type enforcement and single metric calculation."""
        setup = self.get_setup(user_id)

        if field == "goal":
            if not setup.method:
                raise ValueError("Method must be set before setting a goal.")
            field = self.goal_field_map[setup.method]

        value = self.enforce_type(field, value)
        setattr(setup, field, value)

        if setup.tokes and setup.method:
            if setup.method == "number" and setup.reduce_amount is not None:
                setup.reduce_percent = self.__calc_metric__(setup.reduce_amount, setup.tokes)
            elif setup.method == "percent" and setup.reduce_percent is not None:
                setup.reduce_amount = int(self.__calc_metric__(setup.reduce_percent, setup.tokes, to_amount=True))

        setup.updated_at = datetime.now()
        return setup

    def setup_dict(self, user_id: int) -> Dict[int, Dict]:
        """return setup data as a dict, either for data processing or other purposes"""
        setup = self.get_setup(user_id)
        return {user_id: asdict(setup)}
    
    def summary(self, user_id: int) -> str:
        """format a summary for user confirmation"""
        setup = self.get_setup(user_id)
        return (
            f"Tokes: {setup.tokes if setup.tokes is not None else 'Not set'}\n"
            f"Strength: {setup.strength.capitalize() if setup.strength else 'Not set'}\n"
            f"Method: {setup.method.capitalize() if setup.method else 'Not set'}\n"
            f"Reduce Amount: {setup.reduce_amount if setup.reduce_amount is not None else 'Not set'}\n"
            f"Reduce Percent: {setup.reduce_percent if setup.reduce_percent is not None else 'Not set'}%"
        )
