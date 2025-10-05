from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from telegram import Update, MessageEntity
import re

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
    """telegram session data, this likely needs"""
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
    
    @property
    def reply_text(self) -> Optional[str]:
        return self.message.reply
    
@dataclass
class SetupData:
    tokes: Optional[int] = None
    strength: Optional[str] = None
    method: Optional[str] = None
    reduce_amount: Optional[int] = None
    reduce_percent: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class DataParser:
    """utility class for parsing and validating dtypes."""
    @staticmethod
    def to_int(value: Any) -> int:
        """parse integers from strings, floats, or other types."""
        if value is None:
            raise ValueError("Integer value cannot be None")
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(round(value))
        if isinstance(value, str):
            match = re.search(r'-?\d+', value)  # allow negative numbers
            if match:
                return int(match.group())
            raise ValueError(f"No integer found in string '{value}'")
        raise ValueError(f"Cannot convert {type(value)} to int")

    @staticmethod
    def to_float(value: Any) -> float:
        """parse floats from strings, ints, or other types."""
        if value is None:
            raise ValueError("Float value cannot be None")
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        if isinstance(value, str):
            match = re.search(r'-?\d+(\.\d+)?', value.replace(',', ''))
            if match:
                return float(match.group())
            raise ValueError(f"No float found in string '{value}'")
        raise ValueError(f"Cannot convert {type(value)} to float")

    @staticmethod
    def to_str(value: Any) -> str:
        """ensure the value is a string and strip whitespace."""
        if value is None:
            raise ValueError("String value cannot be None")
        return str(value).strip()

    @staticmethod
    def to_datetime(value: Any) -> datetime:
        """parse datetime from string"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Cannot parse datetime from string '{value}'")
        raise ValueError(f"Cannot convert {type(value)} to datetime")
    
    @classmethod
    def enforce_type(cls, field_type: type, value: Any, field_name: str) -> Any:
        """Dispatch to correct type parser"""
        if field_type in (int, Optional[int]):
            return cls.to_int(value, field_name)
        if field_type in (float, Optional[float]):
            return cls.to_float(value, field_name)
        if field_type in (str, Optional[str]):
            return cls.to_str(value, field_name)
        if field_type in (datetime, Optional[datetime]):
            return cls.to_datetime(value, field_name)
        return value

class SetupManager:
    def __init__(self):
        self.setups: Dict[int, SetupData] = {}
        self.parser = DataParser()  # type enforcement lives here
        self.goal_field_map = {
            "number": "reduce_amount", 
            "percent": "reduce_percent"
        }

    def __calc_metric__(self, numerator: float, denominator: float, to_amount: bool = False) -> Optional[float]:
        """dunder method to calculate either percentage or absolute amount"""
        if denominator == 0:
            return None
        return round((numerator / 100 * denominator) if to_amount else (numerator / denominator * 100), 2)

    def get_setup(self, user_id: int) -> SetupData:
        if user_id not in self.setups:
            self.setups[user_id] = SetupData()
        return self.setups[user_id]

    def update_setup_field(self, user_id: int, field: str, value) -> SetupData:
        """update a user’s setup field with parsing and metric calculation"""
        setup = self.get_setup(user_id)

        # handle goal mapping
        if field == "goal":
            if not setup.method:
                raise ValueError("Method must be set before setting a goal.")
            field = self.goal_field_map[setup.method]

        # parse value according to target type
        if field in ("reduce_amount", "tokes"):
            value = self.parser.to_int(value)
        elif field == "reduce_percent":
            value = self.parser.to_float(value)
        elif field == "strength":
            value = self.parser.to_int(value)
        elif field in ("method",):
            value = str(value)
        elif field in ("created_at", "updated_at"):
            value = value if isinstance(value, datetime) else datetime.fromisoformat(value)

        setattr(setup, field, value)

        # recalc complementary metric
        if setup.tokes and setup.method:
            if setup.method == "number" and setup.reduce_amount is not None:
                setup.reduce_percent = self.__calc_metric__(setup.reduce_amount, setup.tokes)
            elif setup.method == "percent" and setup.reduce_percent is not None:
                setup.reduce_amount = int(self.__calc_metric__(setup.reduce_percent, setup.tokes, to_amount=True))

        setup.updated_at = datetime.now()
        return setup

    def setup_dict(self, user_id: int) -> Dict[int, Dict]:
        setup = self.get_setup(user_id)
        return {user_id: asdict(setup)}

    def summary(self, user_id: int) -> str:
        """format a summary for user confirmation with units"""
        setup = self.get_setup(user_id)
        return (
            f"Tokes: {setup.tokes if setup.tokes is not None else 'Not set'} puffs\n"
            f"Strength: {str(setup.strength) + 'mg' if setup.strength is not None else 'Not set'}\n"
            f"Method: {setup.method.capitalize() if setup.method else 'Not set'}\n"
            f"Reduce Amount: {setup.reduce_amount if setup.reduce_amount is not None else 'Not set'} puffs\n"
            f"Reduce Percent: {setup.reduce_percent if setup.reduce_percent is not None else 'Not set'}%"
        )

