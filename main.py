import math
import sys

import pygame
from pygame.locals import *

import hh_py.input as x360
from hh_py.entity import Entity
# from hh_py.tile_map import TileMap
from hh_py.game_state import *
from copy import copy, deepcopy
from time import time
from hh_py.ai import SimpleGraph, SquareGrid, WeightedGrid, Queue, PriorityQueue

pygame.init()

RESOLUTION = (960, 540)
SURFACE = pygame.display.set_mode(RESOLUTION, 0, 32)
pygame.display.set_caption('handmade_hero_py')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

FPS = 60
CLOCK = pygame.time.Clock()


# TODO: move to 'intrinsics.py'


def truncate_float(f):
    return int(f)


def floor_float(f):
    result = math.floor(f)
    return result


def round_float_to_int(f):
    return int(f + 0.5)


# TODO: sin(angle)
# TODO: cos(angle)
# TODO: atan2(y, x)

def get_controller(index):
    result = None
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        result = x360.Controller(index)
    return result


def draw_rectangle(buffer, x, y, width, height, colour):
    min_x = round_float_to_int(x)  # - (width / 2)  # this seems wrong lol
    min_y = round_float_to_int(y)  # - (height / 2)  # this seems wrong lol
    max_x = round_float_to_int(width)
    max_y = round_float_to_int(height)

    if min_x < 0:
        min_x = 0
    if min_y < 0:
        min_y = 0
    if max_x > buffer.get_width():
        max_x = buffer.get_width()
    if max_y > buffer.get_width():
        max_y = buffer.get_width()

    pygame.draw.rect(buffer, colour, (min_x, min_y, max_x, max_y))


def draw_debug_text(world, contents, entity, x_offset=0, y_offset=0):
    font = pygame.font.Font('freesansbold.ttf', 10)
    text_surface = font.render(contents, True, WHITE, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.left = entity.pos.tile_x * world.tile_side_in_pixels  # x_offset + (world.metres_to_pixels * world.lower_left_x) + (world.tile_side_in_pixels * entity.pos.tile_x) + (world.metres_to_pixels * entity.pos.x) + (world.metres_to_pixels * entity.width)
    text_rect.top = entity.pos.tile_y * world.tile_side_in_pixels  # y_offset + (world.metres_to_pixels * world.lower_left_y) + (world.tile_side_in_pixels * entity.pos.tile_y) + (world.metres_to_pixels * entity.pos.y)
    SURFACE.blit(text_surface, text_rect)


def is_tile_map_point_empty(world, tile_map, test_tile_x, test_tile_y):
    is_empty = False

    if tile_map:
        if 0 <= test_tile_x < world.count_x and 0 <= test_tile_y < world.count_y:
            tile = get_tile_value_unchecked(world, tile_map, test_tile_x, test_tile_y)  # [test_tile_y * tile_map.count_x + test_tile_x]
            is_empty = tile is 0

    return is_empty


def is_world_point_empty(world, pos):  # test_raw_position):
    # pos = get_canonical_position(world, test_raw_position)
    tile_map = get_tile_map(world, pos.tile_map_x, pos.tile_map_y)
    is_empty = is_tile_map_point_empty(world, tile_map, pos.tile_x, pos.tile_y)

    return is_empty


def get_tile_value_unchecked(world, tile_map, tile_x, tile_y):
    # assert tile_map
    # assert 0 <= tile_x < world.count_x and 0 <= tile_y < world.count_y

    tile = tile_map.tiles[tile_y][tile_x]

    return tile


def get_tile_map(world, tile_map_x, tile_map_y):
    tile_map = None

    if 0 <= tile_map_x < world.tile_map_count_x and \
            0 <= tile_map_y < world.tile_map_count_y:
        tile_map = world.tile_maps[tile_map_y][tile_map_x]

    return tile_map


def canon_coord(world, tile_count, tile_map, tile, rel):
    offset = floor_float(rel / world.tile_side_in_metres)  # world.tile_side_in_pixels  # truncate_float(x / world.tile_width)
    tile += offset
    rel -= offset * world.tile_side_in_metres  # world.tile_side_in_pixels

    assert rel >= 0
    assert rel <= world.tile_side_in_metres  # world.tile_side_in_pixels

    if tile < 0:
        tile = tile_count + tile
        tile_map = tile_map - 1

    if tile >= tile_count:
        tile = tile - tile_count
        tile_map = tile_map + 1

    return tile_map, tile, rel


def re_canonical_position(world, old_pos):
    result = deepcopy(old_pos)

    result.tile_map_x, result.tile_x, result.x = canon_coord(world, world.count_x, result.tile_map_x, result.tile_x, result.x)
    result.tile_map_y, result.tile_y, result.y = canon_coord(world, world.count_y, result.tile_map_y, result.tile_y, result.y)

    return result


# old
def get_canonical_position(world, raw_position):
    result = WorldPosition()

    result.tile_map_x = raw_position.tile_map_x
    result.tile_map_y = raw_position.tile_map_y

    x = raw_position.x - world.upper_left_x
    y = raw_position.y - world.upper_left_y
    result.tile_x = floor_float(x / world.tile_side_in_pixels)  # truncate_float(x / world.tile_width)
    result.tile_y = floor_float(y / world.tile_side_in_pixels)  # truncate_float(y / world.tile_height)

    result.x = x - result.tile_x * world.tile_side_in_pixels
    result.y = y - result.tile_y * world.tile_side_in_pixels

    assert result.x >= 0
    assert result.y >= 0
    assert result.x < world.tile_side_in_pixels
    assert result.y < world.tile_side_in_pixels

    if result.tile_x < 0:
        result.tile_x = world.count_x + result.tile_x
        result.tile_map_x = result.tile_map_x - 1

    if result.tile_y < 0:
        result.tile_y = world.count_y + result.tile_y
        result.tile_map_y = result.tile_map_y - 1

    if result.tile_x >= world.count_x:
        result.tile_x = result.tile_x - world.count_x
        result.tile_map_x = result.tile_map_x + 1

    if result.tile_y >= world.count_y:
        result.tile_y = result.tile_y - world.count_y
        result.tile_map_y = result.tile_map_y + 1

    return result


def update_familiar(familiar, player):
    delta_pos_x = abs(player.x - familiar.x)
    delta_pos_y = abs(player.y - familiar.y)

    if delta_pos_x > 50 or delta_pos_y > 50:
        if player.x > familiar.x:
            familiar.x += 2
        if player.x < familiar.x:
            familiar.x -= 2
        if player.y > familiar.y:
            familiar.y += 2
        if player.y < familiar.y:
            familiar.y -= 2


def update_baddy(level, baddy, player):
    delta_pos_x = abs(player.x - baddy.x)
    delta_pos_y = abs(player.y - baddy.y)

    if delta_pos_x < 70 or delta_pos_y < 70:
        baddy.state = 'ATTACKING'
        new_pos_x = baddy.x
        new_pos_y = baddy.y

        if player.x > baddy.x:
            new_pos_x += 1
        if player.x < baddy.x:
            new_pos_x -= 1
        if player.y > baddy.y:
            new_pos_y += 1
        if player.y < baddy.y:
            new_pos_y -= 1

        if is_tile_map_point_empty(level, new_pos_x, new_pos_y) and \
                is_tile_map_point_empty(level, new_pos_x + baddy.width, new_pos_y) and \
                is_tile_map_point_empty(level, new_pos_x, new_pos_y + baddy.height) and \
                is_tile_map_point_empty(level, new_pos_x + baddy.width, new_pos_y + baddy.height):
            baddy.x = new_pos_x
            baddy.y = new_pos_y
    else:
        baddy.state = 'no target'


def main():
    if pygame.joystick.get_count() > 0:
        gamepads = [x360.Controller(i) for i in pygame.joystick.get_count()]
    else:
        print('> no controllers found. use keyboard for input.')

    # ----- SETUP ----- #

    # TODO: Pretty sure we're at episode 33 - virtualised tile maps

    tiles_0_0 = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    tiles_0_1 = [
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    tiles_1_0 = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    tiles_1_1 = [
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    tiles_mega = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    tile_maps = [
        [TileMap(tiles_mega)]
        # [TileMap(tiles_0_0), TileMap(tiles_1_0)],
        # [TileMap(tiles_0_1), TileMap(tiles_1_1)]
    ]

    world = World()
    world.count_x = 17 * 2
    world.count_y = 9 * 2
    world.tile_map_count_x = len(tile_maps[0])
    world.tile_map_count_y = len(tile_maps)
    world.tile_side_in_metres = 1
    world.tile_side_in_pixels = 60
    world.metres_to_pixels = world.tile_side_in_pixels / world.tile_side_in_metres
    world.lower_left_x = -(world.tile_side_in_pixels / 2)
    world.lower_left_y = SURFACE.get_height()
    world.tile_maps = tile_maps

    player = Entity(0.75*world.tile_side_in_metres, world.tile_side_in_metres)
    player.pos.tile_map_x = 0
    player.pos.tile_map_y = 0
    player.pos.tile_x = 14
    player.pos.tile_y = 4
    player.pos.x = 0.1
    player.pos.y = 0.1

    familiar = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)

    baddy = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    baddy.pos.tile_map_x = 0
    baddy.pos.tile_map_y = 0
    baddy.pos.tile_x = 5
    baddy.pos.tile_y = 5
    baddy.pos.x = 1
    baddy.pos.y = 1

    baddy_2 = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    baddy_2.pos.tile_map_x = 0
    baddy_2.pos.tile_map_y = 0
    baddy_2.pos.tile_x = 10
    baddy_2.pos.tile_y = 1
    baddy_2.pos.x = 1
    baddy_2.pos.y = 1

    current_tile_map = get_tile_map(world, player.pos.tile_map_x, player.pos.tile_map_y)
    assert current_tile_map

    while True:
        delta = CLOCK.get_time() / 1000

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # TODO: using keyboard input, modify for x360
        keys = pygame.key.get_pressed()

        player_x_delta = 0
        player_y_delta = 0

        if keys[K_UP] is 1:
            player_y_delta = 1
        if keys[K_DOWN] is 1:
            player_y_delta = -1
        if keys[K_LEFT] is 1:
            player_x_delta = -1
        if keys[K_RIGHT] is 1:
            player_x_delta = 1

        player_x_delta *= 10
        player_y_delta *= 10

        # TODO: diagonal will be faster - fixed with vectors
        new_player_pos = deepcopy(player.pos)
        new_player_pos.x += (delta * player_x_delta)
        new_player_pos.y += (delta * player_y_delta)
        new_player_pos = re_canonical_position(world, new_player_pos)

        # player_left = player.pos
        # player_left.x -= 0.5 * player.width
        # player_left = re_canonical_position(world, player_left)
        #
        # player_right = player.pos
        # player_right.x += 0.5 * player.width
        # player_right = re_canonical_position(world, player_right)

        if is_world_point_empty(world, new_player_pos):
            player.pos = deepcopy(new_player_pos)

        # ----- UPDATE ----- #

        current_tile_map = get_tile_map(world, player.pos.tile_map_x, player.pos.tile_map_y)
        assert current_tile_map

        baddy.mov.update(re_canonical_position, world, current_tile_map, baddy, player, delta)
        baddy_2.mov.update(re_canonical_position, world, current_tile_map, baddy_2, player, delta)

        # ----- RENDER ----- #

        draw_rectangle(SURFACE, 0, 0, SURFACE.get_width(), SURFACE.get_height(), BLACK)

        y_start = -10
        y_end = 10
        x_start = -20
        x_end = 20

        centre_x = SURFACE.get_width() / 2
        centre_y = SURFACE.get_height() / 2

        for y in range(y_start, y_end):  # world.count_y):
            for x in range(x_start, x_end):  # world.count_x):
                column = x + player.pos.tile_x
                row = y + player.pos.tile_y

                print('[x,y]: {}, {}, [p.t_x,_y]: {}, {}, [row, col]: {}, {}'.format(x, y, player.pos.tile_x, player.pos.tile_y, row, column))
                tile = get_tile_value_unchecked(world, current_tile_map, column, row)  # x, y)
                grey = (125, 125, 125)
                if tile is 1:
                    grey = (255, 255, 255)
                if x == player.pos.tile_x and y == player.pos.tile_y or \
                        x == baddy.pos.tile_x and y == baddy.pos.tile_y or \
                        x == baddy_2.pos.tile_x and y == baddy_2.pos.tile_y:
                    grey = (0, 0, 0)
                if (x, y) in baddy.mov.path:
                    grey = (50, 50, 50)
                if (x, y) in baddy_2.mov.path:
                    grey = (50, 50, 50)

                min_x = centre_x - world.metres_to_pixels * player.pos.x + x*world.tile_side_in_pixels
                min_y = centre_y + world.metres_to_pixels * player.pos.y - y*world.tile_side_in_pixels
                max_x = world.tile_side_in_pixels
                max_y = -world.tile_side_in_pixels
                draw_rectangle(SURFACE, min_x, min_y, max_x, max_y, grey)

        # draw entities
        player_left = centre_x - 0.5 * world.metres_to_pixels * player.width
        player_top = centre_y - world.metres_to_pixels * player.height
        draw_rectangle(SURFACE,
                       player_left, player_top,
                       world.metres_to_pixels*player.width,
                       world.metres_to_pixels*player.height,
                       BLUE)

        # draw_rectangle(SURFACE, familiar.x, familiar.y, familiar.width, familiar.height, GREEN)
        baddy_1_left = world.lower_left_x + world.tile_side_in_pixels * baddy.pos.tile_x + \
                       world.metres_to_pixels * baddy.pos.x - 0.5 * world.metres_to_pixels * baddy.width
        baddy_1_top = world.lower_left_y - world.tile_side_in_pixels * baddy.pos.tile_y - \
                      world.metres_to_pixels * baddy.pos.y - world.metres_to_pixels * baddy.height
        draw_rectangle(SURFACE,
                       baddy_1_left, baddy_1_top,
                       world.metres_to_pixels*baddy.width,
                       world.metres_to_pixels*baddy.height,
                       RED)

        baddy_2_left = world.lower_left_x + world.tile_side_in_pixels * baddy_2.pos.tile_x + \
                       world.metres_to_pixels * baddy_2.pos.x - 0.5 * world.metres_to_pixels * baddy_2.width
        baddy_2_top = world.lower_left_y - world.tile_side_in_pixels * baddy_2.pos.tile_y - \
                      world.metres_to_pixels * baddy_2.pos.y - world.metres_to_pixels * baddy_2.height
        draw_rectangle(SURFACE,
                       baddy_2_left, baddy_2_top,
                       world.metres_to_pixels*baddy_2.width,
                       world.metres_to_pixels*baddy_2.height,
                       RED)

        # # player debug info
        draw_debug_text(world, 'player: {}, {}'.format(player.pos.tile_x, player.pos.tile_y), player)
        # draw_debug_text(world, 'x: {}'.format(player.pos.x), player, y_offset=10)
        # draw_debug_text(world, 'y: {}'.format(player.pos.y), player, y_offset=20)
        # draw_debug_text(world, 'pet: {}, {}'.format(familiar.x, familiar.y), familiar)
        # draw_debug_text(world, 'baddy: {}, {} : {}'.format(baddy.x, baddy.y, baddy.state), baddy)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == '__main__':
    main()
