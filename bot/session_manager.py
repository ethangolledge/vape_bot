from typing import Dict, Optional
from datetime import datetime
from telegram import Update
from .models import SessionData, SetupData
from .extractors import TelegramExtractor

class SessionManager:
    """Manages user sessions and setup data separately"""
    
    def __init__(self):
        self.sessions: Dict[int, SessionData] = {}
        self.setup_data: Dict[int, SetupData] = {}
        self.extractor = TelegramExtractor()
    
    def get_session(self, up: Update) -> SessionData:
        """Get existing session or create new one"""
        user_id = self.extractor.extract_user(up).user_id
        
        if user_id not in self.sessions:
            self.sessions[user_id] = self.extractor.create_session(up)
        else:
            # Update message data for current interaction
            self.sessions[user_id].message = self.extractor.extract_message(up)
        
        return self.sessions[user_id]
    
    def get_setup_data(self, user_id: int) -> SetupData:
        """Get setup data for user, create if doesn't exist"""
        if user_id not in self.setup_data:
            self.setup_data[user_id] = SetupData()
        return self.setup_data[user_id]
    
    def update_setup_field(self, user_id: int, field: str, value: str) -> None:
        """Update a specific setup field"""
        setup = self.get_setup_data(user_id)
        setattr(setup, field, value)
        setup.updated_at = datetime.now()
    
    def get_setup_for_storage(self, user_id: int) -> Optional[SetupData]:
        """Get setup data for user (for storage/processing)"""
        return self.setup_data.get(user_id)
    
    def set_setup_data(self, user_id: int, setup_data: SetupData) -> None:
        """Set complete setup data for user"""
        self.setup_data[user_id] = setup_data
    
    def is_setup_complete(self, user_id: int) -> bool:
        """Check if user has completed setup"""
        setup = self.setup_data.get(user_id)
        return setup.is_complete() if setup else False
    
    def clear_session(self, user_id: int) -> None:
        """Remove session data only"""
        self.sessions.pop(user_id, None)
    
    def clear_setup(self, user_id: int) -> None:
        """Remove setup data only"""
        self.setup_data.pop(user_id, None)
    
    def clear_all_user_data(self, user_id: int) -> None:
        """Remove both session and setup data"""
        self.clear_session(user_id)
        self.clear_setup(user_id)