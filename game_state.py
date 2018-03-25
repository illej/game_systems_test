class World(object):
    def __init__(self):
        self.chunk_shift = 0
        self.chunk_mask = 0
        self.chunk_dim = 0

        self.tile_side_in_metres = 0
        self.tile_side_in_pixels = 0
        self.metres_to_pixels = 0

        self.tile_chunk_count_x = 0
        self.tile_chunk_count_y = 0

        self.tile_chunks = list()


class TileChunk(object):
    def __init__(self, tiles):
        self.tiles = tiles


class TileChunkPosition(object):
    def __init__(self):
        self.tile_chunk_x = 0
        self.tile_chunk_y = 0
        self.rel_tile_x = 0
        self.rel_tile_y = 0


class WorldPosition(object):
    def __init__(self):
        self.abs_tile_x = 0
        self.abs_tile_y = 0
        # TODO: maybe rename to offset x and y
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


