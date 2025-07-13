from dataclasses import dataclass
from typing import Optional
from datetime import datetime

"""Data model for storing user information in the vape bot.
   I think eventually I need to split these into seperate classes,
   as this has the potential to get a bit messy"""
@dataclass
class UserData:
    """General telegram user data"""
    user_id: int
    chat_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None

    """Setup specific user data"""
    tokes: str = None
    strength: str = None
    method: str = None
    goal: str = None

    def summary(self) -> str:
        """Return a summary of the user's setup data."""
        return (
            f"Tokes: {self.tokes.capitalize() if self.tokes else self.tokes}\n"
            f"Strength: {self.strength.capitalize() if self.strength else self.strength}\n"
            f"Method: {self.method.capitalize() if self.method else self.method}\n"
            f"Goal: {(self.goal + '%') if self.goal and self.method == 'percent' else self.goal}"
        )
