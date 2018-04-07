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
        self.rel_x = 0  # tile-relative x and y
        self.rel_y = 0


