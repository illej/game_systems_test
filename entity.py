from .game_state import WorldPosition
from .ai import MovementComponent


class Entity(object):
    def __init__(self, w=1, h=1):
        self.pos = WorldPosition()
        self.mov = MovementComponent()
        self.width = w
        self.height = h
        self.facing_direction = None
        self.state = '..'
        self.colour = None
        self.exists = False
