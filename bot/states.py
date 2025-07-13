from enum import Enum, auto
class BotStates(Enum):
    """The below are states for the setup conversation handler."""
    TOKES = auto()
    STRENGTH = auto()
    METHOD = auto()
    GOAL = auto()