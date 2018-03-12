from .game_state import WorldPosition
from .ai import MovementComponent


class Entity(object):
    def __init__(self, w, h):
        self.pos = WorldPosition()
        self.mov = MovementComponent()
        self.width = w
        self.height = h
        self.facing = None
        self.state = '..'
        self.R = 0
        self.G = 0
        self.B = 0