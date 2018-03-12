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


class World(object):
    count_x = 0
    count_y = 0

    upper_left_x = 0
    upper_left_y = 0
    tile_width = 0
    tile_height = 0

    tile_map_count_x = 0
    tile_map_count_y = 0

    tile_maps = list()


class CanonicalPosition(object):
    pass


class RawPosition(object):
    pass
