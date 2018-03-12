class World(object):
    def __init__(self):
        self.tile_side_in_metres = 0
        self.tile_side_in_pixels = 0
        self.metres_to_pixels = 0
        self.count_x = 0
        self.count_y = 0
        self.upper_left_x = 0
        self.upper_left_y = 0
        self.tile_width = 0
        self.tile_height = 0
        self.tile_map_count_x = 0
        self.tile_map_count_y = 0
        self.tile_maps = list()


class TileMap(object):
    def __init__(self, tiles):
        self.tiles = tiles


class WorldPosition(object):
    def __init__(self):
        self.tile_map_x = 0
        self.tile_map_y = 0
        self.tile_x = 0
        self.tile_y = 0
        self.x = 0  # tile-relative x and y
        self.y = 0


class GameInput(object):
    mouse_buttons = list()
    mouse_x = 0
    mouse_y = 0
    mouse_z = 0
    delta_time = 0
    controllers = list()


class GameButtonState(object):
    def __init__(self):
        self.half_transition_count = 0
        self.ended_down = False


class GameControllerInput(object):
    is_connected = False
    is_analog = False
    stick_average_x = 0
    stick_average_y = 0
    move_up = GameButtonState()
    move_down = GameButtonState()
    move_left = GameButtonState()
    move_right = GameButtonState()


