class UserData:
    """The plan is to have a user data class that can store interaction data."""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.tokes = None
        self.strength = None
        self.method = None
        self.goal = None

    def summary(self):
        return (
            f"Tokes: {self.tokes}\n"
            f"Strength: {self.strength}\n"
            f"Method: {self.method}\n"
            f"Goal: {self.goal}"
        )
