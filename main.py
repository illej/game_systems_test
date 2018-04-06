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


# def draw_debug_text(world, contents, entity, x_offset=0, y_offset=0):
#     font = pygame.font.Font('freesansbold.ttf', 10)
#     text_surface = font.render(contents, True, WHITE, BLACK)
#     text_rect = text_surface.get_rect()
#     text_rect.left = x_offset + (world.metres_to_pixels * world.lower_left_x) + (world.tile_side_in_pixels * entity.pos.tile_x) + (world.metres_to_pixels * entity.pos.x) + (world.metres_to_pixels * entity.width)
#     text_rect.top = y_offset + (world.metres_to_pixels * world.lower_left_y) + (world.tile_side_in_pixels * entity.pos.tile_y) + (world.metres_to_pixels * entity.pos.y)
#     SURFACE.blit(text_surface, text_rect)


# OK !!
def get_tile_chunk(world, tile_chunk_x, tile_chunk_y):
    tile_chunk = 0

    if 0 <= tile_chunk_x < world.tile_chunk_count_x and \
            0 <= tile_chunk_y < world.tile_chunk_count_y:
        tile_chunk = world.tile_chunks[tile_chunk_y * world.tile_chunk_count_x + tile_chunk_x]  # .tiles[tile_chunk_y][tile_chunk_x]

    return tile_chunk


# OK !!
def get_tile_value_unchecked(world, tile_chunk, tile_x, tile_y):
    # TODO: do we need asserts here?
    assert 0 <= tile_x < world.chunk_dim
    assert 0 <= tile_y < world.chunk_dim

    tile_chunk_value = tile_chunk.tiles[tile_y][tile_x]

    return tile_chunk_value


# OK !!
def get_actual_tile_value(world, tile_chunk, test_tile_x, test_tile_y):
    tile_chunk_value = 0  # type 'int'

    if tile_chunk:  # isinstance(tile_chunk, TileChunk):
        tile_chunk_value = get_tile_value_unchecked(world, tile_chunk, test_tile_x, test_tile_y)

    return tile_chunk_value


# OK !!
def re_coord(world, tile, rel):
    offset = floor_float(rel / world.tile_side_in_metres)
    tile += offset
    rel -= offset * world.tile_side_in_metres

    assert rel >= 0
    assert rel <= world.tile_side_in_metres  # TODO: fix floating point math

    return tile, rel


# OK !!
def re_canonical_position(world, old_pos):
    result = deepcopy(old_pos)

    result.abs_tile_x, result.x = re_coord(world, result.abs_tile_x, result.x)
    result.abs_tile_y, result.y = re_coord(world, result.abs_tile_y, result.y)

    return result


# OK !!
def get_chunk_position_for(world, abs_tile_x, abs_tile_y):
    result = TileChunkPosition()

    result.tile_chunk_x = abs_tile_x >> world.chunk_shift
    result.tile_chunk_y = abs_tile_y >> world.chunk_shift
    result.rel_tile_x = abs_tile_x & world.chunk_mask
    result.rel_tile_y = abs_tile_y & world.chunk_mask

    # result.tile_chunk_x = floor_float(abs_tile_x / world.chunk_dim)
    # result.tile_chunk_y = floor_float(abs_tile_y / world.chunk_dim)
    # result.rel_tile_x = abs_tile_x % world.chunk_dim
    # result.rel_tile_y = abs_tile_y % world.chunk_dim

    return result


# OK !!
def get_tile_value(world, abs_tile_x, abs_tile_y):
    chunk_pos = get_chunk_position_for(world, abs_tile_x, abs_tile_y)
    tile_chunk = get_tile_chunk(world, chunk_pos.tile_chunk_x, chunk_pos.tile_chunk_y)
    tile_chunk_value = get_actual_tile_value(world, tile_chunk, chunk_pos.rel_tile_x, chunk_pos.rel_tile_y)

    return tile_chunk_value


# OK !!
def is_world_point_empty(world, pos):
    tile_chunk_value = get_tile_value(world, pos.abs_tile_x, pos.abs_tile_y)
    is_empty = tile_chunk_value is 0

    return is_empty


# old
# def get_canonical_position(world, raw_position):
#     result = WorldPosition()
#
#     result.tile_map_x = raw_position.tile_map_x
#     result.tile_map_y = raw_position.tile_map_y
#
#     x = raw_position.x - world.upper_left_x
#     y = raw_position.y - world.upper_left_y
#     result.abs_tile_x = floor_float(x / world.tile_side_in_pixels)  # truncate_float(x / world.tile_width)
#     result.abs_tile_y = floor_float(y / world.tile_side_in_pixels)  # truncate_float(y / world.tile_height)
#
#     result.x = x - result.abs_tile_x * world.tile_side_in_pixels
#     result.y = y - result.abs_tile_y * world.tile_side_in_pixels
#
#     assert result.x >= 0
#     assert result.y >= 0
#     assert result.x < world.tile_side_in_pixels
#     assert result.y < world.tile_side_in_pixels
#
#     if result.abs_tile_x < 0:
#         result.abs_tile_x = world.count_x + result.abs_tile_x
#         result.tile_map_x = result.tile_map_x - 1
#
#     if result.abs_tile_y < 0:
#         result.abs_tile_y = world.count_y + result.abs_tile_y
#         result.tile_map_y = result.tile_map_y - 1
#
#     if result.abs_tile_x >= world.count_x:
#         result.abs_tile_x = result.abs_tile_x - world.count_x
#         result.tile_map_x = result.tile_map_x + 1
#
#     if result.abs_tile_y >= world.count_y:
#         result.abs_tile_y = result.abs_tile_y - world.count_y
#         result.tile_map_y = result.tile_map_y + 1
#
#     return result


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


def main():
    if pygame.joystick.get_count() > 0:
        gamepads = [x360.Controller(i) for i in pygame.joystick.get_count()]
    else:
        print('> no controllers found. use keyboard for input.')

    # ----- SETUP ----- #

    # TODO: Pretty sure we're at episode 33 - virtualised tile maps @ 58mins - debugging
    # TODO: shifting tile code into its own file - ep 34 @ 30 - 40 mins
    # TODO: typedef'd int types - ep 34 @ 50 mins

    temp_tiles = []
    for y in range(256):
        row = []
        for x in range(256):
            row.append(0)
        temp_tiles.append(row)

    tiles = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1,     1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1,     1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,     1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,     1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1,     1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1,     1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1,     1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1,     1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,     1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,     1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    for y in range(len(tiles)):  # 18
        for x in range(len(tiles[0])):  # 34
            if tiles[y][x] is 1:
                temp_tiles[y][x] = 1

    world = World()
    world.chunk_shift = 8
    world.chunk_mask = (1 << world.chunk_shift) - 1  # 255
    world.chunk_dim = 256

    world.tile_chunk_count_x = 1  # 256  # len(tile_chunks[0])
    world.tile_chunk_count_y = 1  # 256  # len(tile_chunks)
    world.tile_side_in_metres = 1
    world.tile_side_in_pixels = 60
    world.metres_to_pixels = world.tile_side_in_pixels / world.tile_side_in_metres

    lower_left_x = -(world.tile_side_in_pixels / 2)
    lower_left_y = SURFACE.get_height()

    tile_chunk = TileChunk(temp_tiles)
    world.tile_chunks.append(tile_chunk)  # = tile_chunk

    player = Entity(0.75*world.tile_side_in_metres, world.tile_side_in_metres)
    # player.pos.tile_chunk_x = 0
    # player.pos.tile_chunk_y = 0
    player.pos.abs_tile_x = 3
    player.pos.abs_tile_y = 3
    player.pos.x = 0.2
    player.pos.y = 0.2

    familiar = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)

    baddy = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    # baddy.pos.tile_chunk_x = 0
    # baddy.pos.tile_chunk_y = 0
    baddy.pos.tile_x = 5
    baddy.pos.tile_y = 5
    baddy.pos.x = 1
    baddy.pos.y = 1

    baddy_2 = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    # baddy_2.pos.tile_chunk_x = 0
    # baddy_2.pos.tile_chunk_y = 0
    baddy_2.pos.tile_x = 10
    baddy_2.pos.tile_y = 1
    baddy_2.pos.x = 1
    baddy_2.pos.y = 1

    # current_tile_chunk = get_tile_chunk(world, player.pos.tile_chunk_x, player.pos.tile_chunk_y)
    # assert current_tile_chunk

    while True:
        delta = CLOCK.get_time() / 1000
        print('delta:', delta)

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

        # current_tile_chunk = get_tile_chunk(world, player.pos.tile_chunk_x, player.pos.tile_chunk_y)
        # assert current_tile_chunk

        # baddy.mov.update(re_canonical_position, world, current_tile_chunk, baddy, player, delta)
        # baddy_2.mov.update(re_canonical_position, world, current_tile_chunk, baddy_2, player, delta)

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
                column = x + player.pos.abs_tile_x
                row = y + player.pos.abs_tile_y

                tile = get_tile_value(world, column, row)
                grey = (125, 125, 125)
                if tile is 1:
                    grey = (255, 255, 255)
                if x == player.pos.abs_tile_x and y == player.pos.abs_tile_y or \
                        x == baddy.pos.abs_tile_x and y == baddy.pos.abs_tile_y or \
                        x == baddy_2.pos.abs_tile_x and y == baddy_2.pos.abs_tile_y:
                    grey = (0, 0, 0)
                if (x, y) in baddy.mov.path:
                    grey = (50, 50, 50)
                if (x, y) in baddy_2.mov.path:
                    grey = (50, 50, 50)

                min_x = centre_x - world.metres_to_pixels*player.pos.x + x*world.tile_side_in_pixels
                min_y = centre_y + world.metres_to_pixels*player.pos.y - y*world.tile_side_in_pixels
                max_x = world.tile_side_in_pixels
                max_y = -world.tile_side_in_pixels
                draw_rectangle(SURFACE, min_x, min_y, max_x, max_y, grey)

        # draw entities
        player_left = centre_x - 0.5*world.metres_to_pixels * player.width
        player_top = centre_y - world.metres_to_pixels * player.height
        draw_rectangle(SURFACE,
                       player_left, player_top,
                       world.metres_to_pixels*player.width,
                       world.metres_to_pixels*player.height,
                       BLUE)

        # draw_rectangle(SURFACE, familiar.x, familiar.y, familiar.width, familiar.height, GREEN)
        # baddy_1_left = lower_left_x + world.tile_side_in_pixels * baddy.pos.abs_tile_x + \
        #                world.metres_to_pixels * baddy.pos.x - 0.5 * world.metres_to_pixels * baddy.width
        baddy_1_left = centre_x - world.metres_to_pixels*player.pos.x + baddy.pos.abs_tile_x*world.tile_side_in_pixels
        # baddy_1_top = lower_left_y - world.tile_side_in_pixels * baddy.pos.abs_tile_y - \
        #               world.metres_to_pixels * baddy.pos.y - world.metres_to_pixels * baddy.height
        baddy_1_top = centre_y + world.metres_to_pixels*player.pos.y - baddy.pos.y*world.tile_side_in_pixels
        draw_rectangle(SURFACE,
                       baddy_1_left, baddy_1_top,
                       world.metres_to_pixels*baddy.width,
                       world.metres_to_pixels*baddy.height,
                       RED)

        baddy_2_left = lower_left_x + world.tile_side_in_pixels * baddy_2.pos.abs_tile_x + \
                       world.metres_to_pixels * baddy_2.pos.x - 0.5 * world.metres_to_pixels * baddy_2.width
        baddy_2_top = lower_left_y - world.tile_side_in_pixels * baddy_2.pos.abs_tile_y - \
                      world.metres_to_pixels * baddy_2.pos.y - world.metres_to_pixels * baddy_2.height
        draw_rectangle(SURFACE,
                       baddy_2_left, baddy_2_top,
                       world.metres_to_pixels*baddy_2.width,
                       world.metres_to_pixels*baddy_2.height,
                       RED)

        # # player debug info
        # draw_debug_text(world, 'player: {}, {}'.format(player.pos.abs_tile_x, player.pos.abs_tile_y), player)
        # draw_debug_text(world, 'x: {}'.format(player.pos.x), player, y_offset=10)
        # draw_debug_text(world, 'y: {}'.format(player.pos.y), player, y_offset=20)
        # draw_debug_text(world, 'pet: {}, {}'.format(familiar.x, familiar.y), familiar)
        # draw_debug_text(world, 'baddy: {}, {} : {}'.format(baddy.x, baddy.y, baddy.state), baddy)

        pygame.display.update()
        CLOCK.tick(FPS)


def re_do_things(tile):
    dim = 100
    map = floor_float(tile / dim)
    rel_tile = tile % dim

    print('tile: {} => map: {}, rel_tile: {}'.format(tile, map, rel_tile))


def mod_test():
    for i in range(0, 400, 15):
        re_do_things(i)


if __name__ == '__main__':
    main()

    # mod_test()
