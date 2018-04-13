class World(object):
    def __init__(self):
        self.tile_size_in_metres = 0
        self.tile_size_in_pixels = 0
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
    def __init__(self):
        self.tile_x = 0
        self.tile_y = 0
        self.tile_z = 0
        self.rel_x = 0  # tile-relative x and y
        self.rel_y = 0


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
        self.camera_pos = None
        self.player_pos = None


class PositionDifference(object):
    def __init__(self):
        self.d_x = 0
        self.d_y = 0
        self.d_z = 0


# math.h
class Vector2(object):
    """"
    >>> v1 = Vector2(1, 1)
    >>> v2 = Vector2(2, 2)
    >>> v3 = v1 + v2
    >>> v3.x
    3
    >>> v3.y
    3
    >>> v4 = -v1
    >>> v4.x
    -1
    >>> v4.y
    -1
    >>> v4[0]
    -1
    >>> v4[1]
    -1
    >>> v5 = v2 * 3
    >>> v5.x
    6
    >>> v5.y
    6
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.elements = [self.x, self.y]

    def __str__(self):
        return str((self.x, self.y))

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
        x = self.x * other
        y = self.y * other

        return Vector2(x, y)

    def __getitem__(self, item):
        return self.elements[item]


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
