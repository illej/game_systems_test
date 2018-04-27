class World(object):
    def __init__(self):
        self.tile_side_in_metres = 0
        self.tile_side_in_pixels = 0
        self.metres_to_pixels = 0
        self.upper_left_x = 0
        self.upper_left_y = 0
        self.tile_width = 0
        self.tile_height = 0
        self.tile_map = list()


class TileMap(object):
    def __init__(self, tiles):
        self.tiles = tiles
        self.tile_count_x = len(self.tiles[0])
        self.tile_count_y = len(self.tiles)


class WorldPosition(object):
    def __init__(self, tile=(0, 0), rel=(0, 0)):
        self.tile = Vector2(tile[0], tile[1])
        self.tile_x = 0
        self.tile_y = 0
        self.tile_z = 0  # for tracking z level for camera
        self.rel = Vector2(rel[0], rel[1])  # TODO: make this protected?
        self.rel_x = 0  # tile-relative x and y
        self.rel_y = 0
        self.d = Vector2(0, 0)
        self.dd = Vector2(0, 0)


class PlayerBitmaps(object):
    def __init__(self):
        self.align_x = 0
        self.align_y = 0
        self.head = None
        self.cape = None
        self.pants = None


class GameState(object):
    def __init__(self):
        self.player_bitmaps = list()
        self.camera_pos = WorldPosition()

        self.player_index_for_controller = [-1 for x in range(4)]
        self.entity_count = 0
        self.entities = list()

        self.camera_following_entity_index = 0


class PositionDifference(object):
    def __init__(self):
        self.d_xy = Vector2(0, 0)
        self.d_z = 0


# math.h
class Vector2(object):
    def __init__(self, x, y):  # TODO: maybe make constructor params default to 0
        self.x = x
        self.y = y
        self.elements = [self.x, self.y]

    def __repr__(self):
        return '<{}.v2 x={}, y={}>'.format(self.__module__, self.x, self.y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y

        return Vector2(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y

        return Vector2(x, y)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __mul__(self, other):
        """
        Multiplies the Vector by a float
        :param other: float
        :return: new Vector product
        """
        x = self.x * other
        y = self.y * other

        return Vector2(x, y)

    def __iadd__(self, other):
        vector = self + other

        return vector

    def __imul__(self, other):
        vector = self * other

        return vector

    def __getitem__(self, item):
        return self.elements[item]


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
