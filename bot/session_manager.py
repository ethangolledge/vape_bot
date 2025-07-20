from typing import Dict, Optional
from telegram import Update
from .models import SessionData, SetupData
from .extractors import TelegramExtractor

class SessionManager:
    """Manages user sessions and setup data separately"""
    
    def __init__(self):
        self.sessions: Dict[int, SessionData] = {}
        self.setup_data: Dict[int, SetupData] = {}
        self.extractor = TelegramExtractor()
    
    def get_session(self, update: Update) -> SessionData:
        """Get existing session or create new one"""
        user_id = self.extractor.extract_user(update).user_id
        
        if user_id not in self.sessions:
            self.sessions[user_id] = self.extractor.create_session(update)
        else:
            # Update message data for current interaction
            self.sessions[user_id].message = self.extractor.extract_message(update)
        
        return self.sessions[user_id]
    
    def get_setup_data(self, user_id: int) -> SetupData:
        """Get setup data for user, creating new instance if needed"""
        if user_id not in self.setup_data:
            self.setup_data[user_id] = SetupData()
        return self.setup_data[user_id]
    
    def update_setup_field(self, user_id: int, field: str, value: str) -> None:
        """Update a specific setup field"""
        setup_data = self.get_setup_data(user_id)
        setattr(setup_data, field, value)
    
    def has_setup_data(self, user_id: int) -> bool:
        """Check if user has any setup data"""
        return user_id in self.setup_data
    
    def is_setup_complete(self, user_id: int) -> bool:
        """Check if user's setup is complete"""
        if not self.has_setup_data(user_id):
            return False
        return self.setup_data[user_id].is_complete()
    
    def clear_session(self, user_id: int) -> None:
        """Remove session data only"""
        self.sessions.pop(user_id, None)
    
    def clear_setup_data(self, user_id: int) -> None:
        """Remove setup data only"""
        self.setup_data.pop(user_id, None)
    
    def clear_all_user_data(self, user_id: int) -> None:
        """Remove both session and setup data"""
        self.clear_session(user_id)
        self.clear_setup_data(user_id)