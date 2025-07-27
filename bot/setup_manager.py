from typing import Dict
from .models import SetupData

class SetupManager:
    def __init__(self):
        self.setups: Dict[int, SetupData] = {}
    
    def get_setup(self, user_id: int) -> SetupData:
        """Get or create setup data for the user"""
        if user_id not in self.setups:
            self.setups[user_id] = SetupData()
        return self.setups[user_id]
    
    def update_setup_field(self, user_id: int, field: str, value: str) -> SetupData:
        """Update a field in the setup data"""
        setup = self.get_setup(user_id)
        setattr(setup, field, value)
        return setup