# from hh_py.game_controller_input import *
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


def subtract(world, a, b):
    result = PositionDifference()

    d_tile_x = a.tile_x - b.tile_x
    d_tile_y = a.tile_y - b.tile_y
    d_tile_z = a.tile_z - b.tile_z

    result.d_x = world.tile_side_in_metres * d_tile_x + (a.rel_x - b.rel_x)
    result.d_y = world.tile_side_in_metres * d_tile_y + (a.rel_y - b.rel_y)
    result.d_z = world.tile_side_in_metres * d_tile_z + 0  # TODO: Not yet implemented

    return result


def get_controller(index):
    result = None
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        result = x360.Controller(index)
    return result


def draw_rectangle(buffer, x, y, width, height, colour, align_x=0, align_y=0):
    x -= align_x
    y -= align_y

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

    pygame.draw.rect(buffer, BLACK, (min_x, min_y, max_x - 1, max_y - 1))
    pygame.draw.rect(buffer, colour, (min_x + 1, min_y + 1, max_x, max_y))


def draw_debug_text(world, contents, entity, x_offset=0, y_offset=0):
    font = pygame.font.Font('freesansbold.ttf', 10)
    text_surface = font.render(contents, True, WHITE, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.left = x_offset + (world.metres_to_pixels * world.upper_left_x) + (world.tile_side_in_pixels * entity.pos.tile_x) + (world.metres_to_pixels * entity.pos.rel_x) + (world.metres_to_pixels * entity.width)
    text_rect.top = y_offset + (world.metres_to_pixels * world.upper_left_y) + (world.tile_side_in_pixels * entity.pos.tile_y) + (world.metres_to_pixels * entity.pos.rel_y)
    SURFACE.blit(text_surface, text_rect)


def is_tile_map_point_empty(world, tile_map, test_tile_x, test_tile_y):
    is_empty = False

    if tile_map:
        if 0 <= test_tile_x < tile_map.tile_count_x and 0 <= test_tile_y < tile_map.tile_count_y:
            tile = get_tile_value_unchecked(world, test_tile_x, test_tile_y)  # [test_tile_y * tile_map.count_x + test_tile_x]
            is_empty = tile is 0

    return is_empty


def is_world_point_empty(world, pos):
    is_empty = is_tile_map_point_empty(world, world.tile_map, pos.tile_x, pos.tile_y)

    return is_empty


def get_tile_value_unchecked(world, tile_x, tile_y):
    # assert world.tile_map
    # assert 0 <= tile_x < world.tile_map.tile_count_x and 0 <= tile_y < world.tile_map.tile_count_y
    tile = -1

    if 0 <= tile_x < world.tile_map.tile_count_x and 0 <= tile_y < world.tile_map.tile_count_y:
        tile = world.tile_map.tiles[tile_y][tile_x]

    return tile


def get_tile_map(world, tile_map_x, tile_map_y):
    tile_map = None

    if 0 <= tile_map_x < world.tile_map_count_x and \
            0 <= tile_map_y < world.tile_map_count_y:
        tile_map = world.tile_maps[tile_map_y][tile_map_x]

    return tile_map


def canon_coord(world, tile, rel):
    offset = floor_float(rel / world.tile_side_in_metres)  # world.tile_side_in_pixels  # truncate_float(x / world.tile_width)
    tile += offset
    rel -= offset * world.tile_side_in_metres  # world.tile_side_in_pixels

    assert rel >= 0
    assert rel <= world.tile_side_in_metres  # world.tile_side_in_pixels

    return tile, rel


def re_canonical_position(world, old_pos):
    result = deepcopy(old_pos)

    result.tile_x, result.rel_x = canon_coord(world, result.tile_x, result.rel_x)
    result.tile_y, result.rel_y = canon_coord(world, result.tile_y, result.rel_y)

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


def weld_maps(maps):
    result = None

    for i, r in enumerate(maps[0][0].tiles):
        r.extend(maps[0][1].tiles[i])

    for i, r in enumerate(maps[1][0].tiles):
        r.extend(maps[1][1].tiles[i])

    maps[0][0].tiles.extend(maps[1][0].tiles)

    result = maps[0][0].tiles

    w = len(result[0])
    h = len(result)
    print('w: {}, h: {}'.format(w, h))

    return result


def main():
    if pygame.joystick.get_count() > 0:
        gamepads = [x360.Controller(i) for i in pygame.joystick.get_count()]
    else:
        print('> no controllers found. use keyboard for input.')

    # ----- SETUP ----- #

    # TODO: episode 42 for replacing scalar value code with 2d vectors. (@ 48 mins)

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

    tile_maps = [
        [TileMap(tiles_0_0), TileMap(tiles_1_0)],
        [TileMap(tiles_0_1), TileMap(tiles_1_1)]
    ]

    tiles = weld_maps(tile_maps)

    for r in tiles:
        print(r)

    # ----- Actual Setup ----- #

    world = World()
    world.tile_side_in_metres = 1
    world.tile_side_in_pixels = 60
    world.metres_to_pixels = world.tile_side_in_pixels / world.tile_side_in_metres
    world.upper_left_x = -(world.tile_side_in_metres / 2)
    world.upper_left_y = 0
    world.tile_map = TileMap(tiles)

    upper_left_x = -(world.tile_side_in_metres / 2)
    upper_left_y = 0

    camera_pos = WorldPosition()
    camera_pos.tile_x = world.tile_map.tile_count_x / 2
    camera_pos.tile_y = world.tile_map.tile_count_y / 2

    player = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    player.pos.tile_x = 3
    player.pos.tile_y = 3
    player.pos.rel_x = 0.5
    player.pos.rel_y = 0.5

    player_bitmap = PlayerBitmaps()
    player_bitmap.align_x = world.tile_side_in_pixels / 2
    player_bitmap.align_y = world.tile_side_in_pixels / 2

    baddy = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    baddy.pos.tile_x = 5
    baddy.pos.tile_y = 5
    baddy.pos.rel_x = 0.5
    baddy.pos.rel_y = 0.5

    baddy_2 = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    baddy_2.pos.tile_x = 10
    baddy_2.pos.tile_y = 1
    baddy_2.pos.rel_x = 0.2
    baddy_2.pos.rel_y = 0.2

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
            player_y_delta = -1
        if keys[K_DOWN] is 1:
            player_y_delta = 1
        if keys[K_LEFT] is 1:
            player_x_delta = -1
        if keys[K_RIGHT] is 1:
            player_x_delta = 1

        player_speed = 10  # TODO: move to Entity or GameState?

        player_x_delta *= player_speed
        player_y_delta *= player_speed

        if player_x_delta != 0 and player_y_delta != 0:
            player_x_delta *= 0.7071067811865475

        # TODO: diagonal will be faster - fixed with vectors
        new_player_pos = deepcopy(player.pos)
        new_player_pos.rel_x += (delta * player_x_delta)
        new_player_pos.rel_y += (delta * player_y_delta)
        new_player_pos = re_canonical_position(world, new_player_pos)

        if is_world_point_empty(world, new_player_pos):
            player.pos = deepcopy(new_player_pos)

        # ----- UPDATE ----- #

        baddy.mov.update(re_canonical_position, world, world.tile_map, baddy, player, delta)
        baddy_2.mov.update(re_canonical_position, world, world.tile_map, baddy_2, player, delta)

        # ----- RENDER ----- #

        draw_rectangle(SURFACE, 0, 0, SURFACE.get_width(), SURFACE.get_height(), BLACK)

        y_start = -10
        y_end = 10
        x_start = -20
        x_end = 20

        centre_x = SURFACE.get_width() / 2
        centre_y = SURFACE.get_height() / 2

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                column = x + player.pos.tile_x
                row = y + player.pos.tile_y

                tile = get_tile_value_unchecked(world, column, row)
                grey = (125, 125, 125)

                if tile is 1:
                    grey = (255, 255, 255)
                if (column, row) in baddy.mov.path:
                    grey = (50, 50, 50)
                if (column, row) in baddy_2.mov.path:
                    grey = (50, 50, 50)
                if column == player.pos.tile_x and row == player.pos.tile_y or \
                        column == baddy.pos.tile_x and row == baddy.pos.tile_y or \
                        column == baddy_2.pos.tile_x and row == baddy_2.pos.tile_y:
                    grey = (0, 0, 0)
                if tile is -1:
                    grey = (255, 0, 0)

                min_x = centre_x - world.metres_to_pixels*player.pos.rel_x + x*world.tile_side_in_pixels
                min_y = centre_y - world.metres_to_pixels*player.pos.rel_y + y*world.tile_side_in_pixels
                max_x = world.tile_side_in_pixels
                max_y = world.tile_side_in_pixels
                draw_rectangle(SURFACE, min_x, min_y, max_x, max_y, grey)

        # draw entities
        player_ground_x = centre_x
        player_ground_y = centre_y
        draw_rectangle(SURFACE,
                       player_ground_x, player_ground_y,
                       world.metres_to_pixels*player.width,
                       world.metres_to_pixels*player.height,
                       BLUE,
                       align_x=world.metres_to_pixels*(player.width / 2),
                       align_y=world.metres_to_pixels*(player.height / 2))

        diff = subtract(world, baddy.pos, player.pos)
        baddy_ground_x = centre_x + diff.d_x*world.metres_to_pixels
        baddy_ground_y = centre_y + diff.d_y*world.metres_to_pixels
        draw_rectangle(SURFACE,
                       baddy_ground_x, baddy_ground_y,
                       world.metres_to_pixels * baddy.width,
                       world.metres_to_pixels * baddy.height,
                       RED,
                       align_x=world.metres_to_pixels*(baddy.width / 2),
                       align_y=world.metres_to_pixels*(baddy.height / 2))

        diff = subtract(world, baddy_2.pos, player.pos)
        baddy_2_ground_x = centre_x + diff.d_x * world.metres_to_pixels
        baddy_2_ground_y = centre_y + diff.d_y * world.metres_to_pixels
        draw_rectangle(SURFACE,
                       baddy_2_ground_x, baddy_2_ground_y,
                       world.metres_to_pixels*baddy_2.width,
                       world.metres_to_pixels*baddy_2.height,
                       RED,
                       align_x=world.metres_to_pixels * (baddy_2.width / 2),
                       align_y=world.metres_to_pixels * (baddy_2.height / 2))

        # player debug info

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == '__main__':
    main()
