from dataclasses import dataclass, field, asdict
from typing import Callable, Optional, List, Dict, Any, TypeVar
from datetime import datetime
from telegram import MessageEntity
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
    
    @property
    def datetime(self) -> Optional[datetime]:
        return self.message.timestamp
    
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

class ModelManager:
    """base class for model management operations"""

    T = TypeVar('T')
    @staticmethod
    def update_model_field(
        model_instance: T,
        field: str, 
        value: Any,
        field_parsers: Dict[str, Callable[[Any], Any]],
        post_update_hook: Callable[[T], None] = None
    ) -> T:
        """generic field updater for any model instance"""
        parser = field_parsers.get(field, lambda x: x)
        
        try:
            # parse and set value
            parsed_value = parser(value)
            setattr(model_instance, field, parsed_value)

            # update timestamp
            if hasattr(model_instance, 'updated_at'):
                model_instance.updated_at = datetime.now()

            # run any post-update operations
            if post_update_hook:
                post_update_hook(model_instance)

            return model_instance
    
        except Exception as e:
            raise ValueError(f"Error updating field '{field}': {e}")

    @staticmethod    
    def model_to_dict(model_instance: T) -> dict:
        """convert a dataclass model instance to a dictionary"""
        return asdict(model_instance)

class SetupManager:
    def __init__(self):
        self.setups: Dict[int, SetupData] = {}
        self.parser = DataParser()
        self.goal_field_map = {
            "number": "reduce_amount",
            "percent": "reduce_percent"
        }
        self.field_parsers = {
            "tokes": self.parser.to_int,
            "strength": self.parser.to_int,
            "method": self.parser.to_str,
            "reduce_amount": self.parser.to_int,
            "reduce_percent": self.parser.to_float,
            'created_at': lambda v: v if isinstance(v, datetime) else datetime.fromisoformat(v),
            'updated_at': lambda v: v if isinstance(v, datetime) else datetime.fromisoformat(v)
        }

    def __calc_metric__(self, numerator: float, denominator: float, to_amount: bool = False) -> Optional[float]:
        """calculate either percentage or absolute amount"""
        if denominator == 0:
            return None
        return round((numerator / 100 * denominator) if to_amount else (numerator / denominator * 100), 2)

    def _recalculate_metrics(self, setup: SetupData) -> None:
        """post-update hook for recalculating metrics"""
        if setup.tokes and setup.method:
            if setup.method == "number" and setup.reduce_amount is not None:
                setup.reduce_percent = self.__calc_metric__(setup.reduce_amount, setup.tokes)
            elif setup.method == "percent" and setup.reduce_percent is not None:
                setup.reduce_amount = int(self.__calc_metric__(setup.reduce_percent, setup.tokes, to_amount=True))

    def get_setup(self, user_id: int) -> SetupData:
        if user_id not in self.setups:
            self.setups[user_id] = SetupData()
        return self.setups[user_id]

    def update_setup_field(self, user_id: int, field: str, value: Any) -> SetupData:
        """update a setup field using ModelManager"""
        setup = self.get_setup(user_id)
        
        # handle goal mapping
        if field == "goal":
            if not setup.method:
                raise ValueError("Method must be set before setting a goal.")
            field = self.goal_field_map[setup.method]
        
        return ModelManager.update_model_field(
            model_instance=setup,
            field=field,
            value=value,
            field_parsers=self.field_parsers,
            post_update_hook=self._recalculate_metrics
        )

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

