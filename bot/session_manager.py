from typing import Dict, Optional
from telegram import Update
from .models import SessionData, SetupAnswers
from .extractors import TelegramExtractor

class SessionManager:
    """Manages user sessions and setup data"""
    
    def __init__(self):
        self.sessions: Dict[int, SessionData] = {}
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
    
    def update_setup_field(self, user_id: int, field: str, value: str) -> None:
        """Update a specific setup field"""
        if user_id in self.sessions:
            setattr(self.sessions[user_id].setup, field, value)
    
    def get_setup_data(self, user_id: int) -> Optional[SetupAnswers]:
        """Get setup data for user (for storage/processing)"""
        if user_id in self.sessions:
            return self.sessions[user_id].setup
        return None
    
    def clear_session(self, user_id: int) -> None:
        """Remove session data"""
        self.sessions.pop(user_id, None)