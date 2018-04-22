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

    d_tile_xy = a.tile - b.tile
    d_tile_z = a.tile_z - b.tile_z

    result.d_xy = (d_tile_xy * world.tile_side_in_metres) + (a.rel - b.rel)
    result.d_z = world.tile_side_in_metres * d_tile_z + 0  # TODO: Not yet implemented

    return result


def square(f):
    return f * f


def inner(a, b):
    return a.x * b.x + a.y * b.y


def length_sq(a):
    return inner(a, a)


def absolute_value(f):
    return abs(f)


def square_root(f):
    # return f**(.5)
    return math.sqrt(f)


def minimum(a, b):
    return a if a < b else b


def maximum(a, b):
    return a if a > b else b


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

    pygame.draw.rect(buffer, colour, (min_x, min_y, max_x, max_y))


def draw_debug_text(world, contents, entity=None, x_offset=0, y_offset=0):
    font = pygame.font.SysFont('monospace', 13)
    text_surface = font.render(contents, False, WHITE, BLACK)
    text_rect = text_surface.get_rect()

    if entity:
        text_rect.left = x_offset + (world.metres_to_pixels * world.upper_left_x) + (world.tile_side_in_pixels * entity.pos.tile.x) + (world.metres_to_pixels * entity.pos.rel.x) + (world.metres_to_pixels * entity.width)
        text_rect.top = y_offset + (world.metres_to_pixels * world.upper_left_y) + (world.tile_side_in_pixels * entity.pos.tile.y) + (world.metres_to_pixels * entity.pos.rel.y)
    else:
        text_rect.left = x_offset
        text_rect.top = y_offset

    SURFACE.blit(text_surface, text_rect)


def is_tile_map_point_empty(world, tile_map, test_tile_x, test_tile_y):
    is_empty = False

    if tile_map:
        if 0 <= test_tile_x < tile_map.tile_count_x and 0 <= test_tile_y < tile_map.tile_count_y:
            tile = get_tile_value_unchecked(world, test_tile_x, test_tile_y)  # [test_tile_y * tile_map.count_x + test_tile_x]
            is_empty = tile is 0

    return is_empty


def is_world_point_empty(world, pos):
    is_empty = is_tile_map_point_empty(world, world.tile_map, pos.tile.x, pos.tile.y)

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

    result.tile.x, result.rel.x = canon_coord(world, result.tile.x, result.rel.x)
    result.tile.y, result.rel.y = canon_coord(world, result.tile.y, result.rel.y)

    return result


def centred_tile_point(x, y):
    result = WorldPosition()

    result.tile.x = x
    result.tile.y = y

    return result


def closest_point_in_rectangle(min, max, diff):
    result = None

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


def are_on_same_tile(old_pos, current_pos):
    # TODO: tracking the player through z levels
    pass


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


def get_entity(game_state, index):
    entity = None

    if 0 <= index < game_state.entity_count:
        entity = game_state.entities[index]

    return entity


def add_entity(game_state):
    entity = Entity()

    game_state.entities.append(entity)
    game_state.entity_count = len(game_state.entities)

    entity_index = game_state.entities.index(entity)

    print('f_add_entity():')
    print('entities[]: ', game_state.entities)
    print('entity_count: ', game_state.entity_count)
    print('entity_index: ', entity_index)

    return entity_index


def add_player(game_state, world, controller):
    entity_index = add_entity(game_state)
    controlling_entity = get_entity(game_state, entity_index)

    initialize_player(world, controlling_entity)
    game_state.player_index_for_controller[controller.get_id()] = entity_index

    print('player_index_for_controller[]: ', game_state.player_index_for_controller)

    return controlling_entity


def initialize_player(world, entity):
    # entity = Entity(w=world.tile_side_in_metres * 0.5, h=world.tile_side_in_metres * 0.5)
    entity.exists = True
    entity.pos.tile.x = 3
    entity.pos.tile.y = 3
    entity.pos.rel.x = 0.5
    entity.pos.rel.y = 0.5
    entity.colour = BLUE


def move_player(game_state, world, player, dd_player_pos, delta):
    # TODO: change 'd_' and '.d' to velocity, and 'dd_' and '.dd' to acceleration

    ddP_length = length_sq(dd_player_pos)
    if ddP_length > 1:  # square of 1 is 1
        dd_player_pos *= (1 / square_root(ddP_length))

    player_speed = 50  # m/s^2 TODO: move to Entity or GameState?
    dd_player_pos *= player_speed
    dd_player_pos += player.pos.d * -10  # friction

    old_player_pos = deepcopy(player.pos)
    new_player_pos = deepcopy(old_player_pos)
    player_delta = (dd_player_pos * 0.5) * square(delta) + (player.pos.d * delta)
    new_player_pos.rel = player_delta + new_player_pos.rel
    new_player_pos.d = (dd_player_pos * delta) + player.pos.d
    new_player_pos = re_canonical_position(world, new_player_pos)

    if 1:  # OLD Collision Detection
        collided = False
        collision_pos = WorldPosition()

        if not is_world_point_empty(world, new_player_pos):
            collision_pos = deepcopy(new_player_pos)
            collided = True

        if collided:
            r = Vector2(0, 0)

            if collision_pos.tile.x < player.pos.tile.x:
                r = Vector2(1, 0)
            if collision_pos.tile.x > player.pos.tile.x:
                r = Vector2(-1, 0)
            if collision_pos.tile.y < player.pos.tile.y:
                r = Vector2(0, 1)
            if collision_pos.tile.y > player.pos.tile.y:
                r = Vector2(0, -1)

            player.pos.d = player.pos.d - r * inner(player.pos.d, r) * 1
        else:
            player.pos = deepcopy(new_player_pos)
    else:
        # NEW Collision Detection
        min_tile_x = minimum(old_player_pos.tile.x, new_player_pos.tile.x)
        min_tile_y = minimum(old_player_pos.tile.y, new_player_pos.tile.y)
        one_past_max_tile_x = maximum(old_player_pos.tile.x, new_player_pos.tile.x) + 1
        one_past_max_tile_y = maximum(old_player_pos.tile.y, new_player_pos.tile.y) + 1

        abs_tile_z = player.pos.tile_z
        t_closest = 1  # length_sq(player_delta)
        tile = Vector2(world.tile_side_in_metres, world.tile_side_in_metres)

        abs_tile_y = min_tile_y
        while abs_tile_y != one_past_max_tile_y:
            abs_tile_y += 1

            abs_tile_x = min_tile_x
            while abs_tile_x != one_past_max_tile_x:
                abs_tile_x += 1

                test_tile_pos = centred_tile_point(abs_tile_x, abs_tile_y)  # add tile.z
                tile_value = get_tile_value_unchecked(world,  # TODO: overload the 'get_tile_*()' ?
                                                      test_tile_pos.tile.x,
                                                      test_tile_pos.tile.y)
                if tile_value is 1:  # function for this?
                    min_corner = tile * -0.5
                    max_corner = tile * 0.5

                    rel_old_player_pos = subtract(world, old_player_pos, test_tile_pos)  # tile v2 is 0, 0
                    rel_movement = rel_old_player_pos.d_xy

                    wall_x = max_corner.x

                    if player_delta.x != 0:
                        t_result = (wall_x - rel_movement.x) / player_delta.x
                        y = rel_movement.y + t_result*player_delta.y

                        if 0 <= t_result < t_closest:
                            if min_corner.y <= y <= max_corner.y:
                                t_closest = t_result
                                # TODO: ep 48 @ 15~ mins


    # Update for camera movement
    if not are_on_same_tile(old_player_pos, player.pos):
        new_tile_value = get_tile_value_unchecked(world, player.pos.tile.x, player.pos.tile.y)

        if new_tile_value is 3:
            player.pos.tile_z += 1
        elif new_tile_value is 4:
            player.pos.tile_z -= 1

    # Determine facing direction
    if absolute_value(player.pos.d.x) > absolute_value(player.pos.d.y):
        if player.pos.d.x > 0:
            player.facing_direction = 1  # east
        else:
            player.facing_direction = 3  # west
    elif absolute_value(player.pos.d.x) < absolute_value(player.pos.d.y):
        if player.pos.d.y > 0:
            player.facing_direction = 2  # south
        else:
            player.facing_direction = 0  # north


class Keyboard(object):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def get_buttons(self):
        return pygame.key.get_pressed()


def main():
    pygame.joystick.init()

    controllers = []
    controller_index = 0

    for i in range(controller_index, pygame.joystick.get_count()):
        controllers.append(x360.Controller(controller_index))
        controller_index += 1

    controllers.append(Keyboard(controller_index))

    if controllers:
        print('> gamepads found ({})'.format(len(controllers)))
        for con in controllers:
            print('\t{} {}'.format(con.get_id(), con))

    __elapsed = 0
    __debug_update_rate = 0.3
    __fps = 0
    __delta = 0

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

    game_state = GameState()

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
    camera_pos.tile.x = world.tile_map.tile_count_x / 2
    camera_pos.tile.y = world.tile_map.tile_count_y / 2

    # player = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    # player.pos.tile.x = 3
    # player.pos.tile.y = 3
    # player.pos.rel.x = 0.5
    # player.pos.rel.y = 0.5
    player = Entity()

    player_bitmap = PlayerBitmaps()
    player_bitmap.align_x = world.tile_side_in_pixels / 2
    player_bitmap.align_y = world.tile_side_in_pixels / 2

    baddy = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    baddy.pos.tile.x = 5
    baddy.pos.tile.y = 5
    baddy.pos.rel.x = 0.5
    baddy.pos.rel.y = 0.5
    baddy.colour = RED
    baddy.exists = True

    # game_state.entities.append(baddy)

    baddy_2 = Entity(world.tile_side_in_metres * 0.5, world.tile_side_in_metres * 0.5)
    baddy_2.pos.tile.x = 10
    baddy_2.pos.tile.y = 1
    baddy_2.pos.rel.x = 0.2
    baddy_2.pos.rel.y = 0.2
    baddy_2.colour = RED
    baddy_2.exists = True

    # game_state.entities.append(baddy_2)

    centre = Vector2(SURFACE.get_width() / 2,
                     SURFACE.get_height() / 2)
    current = Vector2(0, 0)
    min = Vector2(0, 0)
    max = Vector2(world.tile_side_in_pixels,
                  world.tile_side_in_pixels)

    while True:
        delta = CLOCK.get_time() / 1000

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # TODO: ep 47 to finish off player movement

        for controller in controllers:
            entity_index = game_state.player_index_for_controller[controller.get_id()]
            controlling_entity = get_entity(game_state, entity_index)  # controller.get_id())
            if controlling_entity:
                dd_player_pos = Vector2(0, 0)

                if isinstance(controller, x360.Controller):
                    left_x, left_y = controller.get_left_stick()
                    dd_player_pos = Vector2(left_x, left_y)

                elif isinstance(controller, Keyboard):  # is digital (keyboard)
                    keys = controller.get_buttons()

                    if keys[K_UP] is 1:
                        dd_player_pos.y = -1
                    if keys[K_DOWN] is 1:
                        dd_player_pos.y = 1
                    if keys[K_LEFT] is 1:
                        dd_player_pos.x = -1
                    if keys[K_RIGHT] is 1:
                        dd_player_pos.x = 1

                move_player(game_state, world, controlling_entity, dd_player_pos, delta)
            else:
                if isinstance(controller, x360.Controller):
                    start = controller.get_buttons()[7]
                    if start:
                        controlling_entity = add_player(game_state, world, controller)
                        player = controlling_entity  # TODO: this is bad lol
                elif isinstance(controller, Keyboard):
                    start = controller.get_buttons()[K_SPACE]
                    if start:
                        controlling_entity = add_player(game_state, world, controller)
                        player = controlling_entity  # TODO: this is bad lol

        camera_following_entity = get_entity(game_state, game_state.camera_following_entity_index)
        if camera_following_entity:
            game_state.camera_pos.tile_z = camera_following_entity.pos.tile_z

            diff = subtract(world, camera_following_entity.pos, game_state.camera_pos)
            # code to snap camera along x and y tilemaps

        # TODO: pass entity list, and let the AI find valid targets in the list of entities?
        baddy.mov.update(re_canonical_position, world, world.tile_map, baddy, player, delta)
        baddy_2.mov.update(re_canonical_position, world, world.tile_map, baddy_2, player, delta)

        # ----- RENDER ----- #

        draw_rectangle(SURFACE, 0, 0, SURFACE.get_width(), SURFACE.get_height(), BLACK)

        y_start = -10
        y_end = 10
        x_start = -20
        x_end = 20

        # centre = Vector2(SURFACE.get_width() / 2,
        #                  SURFACE.get_height() / 2)

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                column = x + player.pos.tile.x
                row = y + player.pos.tile.y

                tile = get_tile_value_unchecked(world, column, row)
                grey = (125, 125, 125)

                if tile is 1:
                    grey = (255, 255, 255)
                if (column, row) in baddy.mov.path:
                    grey = (50, 50, 50)
                if (column, row) in baddy_2.mov.path:
                    grey = (50, 50, 50)
                if column == player.pos.tile.x and row == player.pos.tile.y or \
                        column == baddy.pos.tile.x and row == baddy.pos.tile.y or \
                        column == baddy_2.pos.tile.x and row == baddy_2.pos.tile.y:
                    grey = (0, 0, 0)
                if tile is -1:
                    grey = (255, 0, 0)

                current.x = x * world.tile_side_in_pixels
                current.y = y * world.tile_side_in_pixels
                min = centre - (player.pos.rel*world.metres_to_pixels) + current
                draw_rectangle(SURFACE, min.x, min.y, max.x, max.y, grey)

        # draw entities TODO: for loop
        player_ground_x = centre.x
        player_ground_y = centre.y
        draw_rectangle(SURFACE,
                       player_ground_x, player_ground_y,
                       world.metres_to_pixels*player.width,
                       world.metres_to_pixels*player.height,
                       BLUE,
                       align_x=world.metres_to_pixels*(player.width / 2),
                       align_y=world.metres_to_pixels*(player.height / 2))

        for e in game_state.entities:
            if e.exists:
                diff = subtract(world, e.pos, player.pos)
                entity_ground_x = centre.x + diff.d_xy.x * world.metres_to_pixels
                entity_ground_y = centre.y + diff.d_xy.y * world.metres_to_pixels
                draw_rectangle(SURFACE,
                               entity_ground_x, entity_ground_y,
                               world.metres_to_pixels * e.width,
                               world.metres_to_pixels * e.height,
                               e.colour,
                               align_x=world.metres_to_pixels * (e.width / 2),
                               align_y=world.metres_to_pixels * (e.height / 2))

        # OLD
        #
        # diff = subtract(world, baddy.pos, player.pos)
        # baddy_ground_x = centre.x + diff.d_xy.x*world.metres_to_pixels
        # baddy_ground_y = centre.y + diff.d_xy.y*world.metres_to_pixels
        # draw_rectangle(SURFACE,
        #                baddy_ground_x, baddy_ground_y,
        #                world.metres_to_pixels * baddy.width,
        #                world.metres_to_pixels * baddy.height,
        #                RED,
        #                align_x=world.metres_to_pixels*(baddy.width / 2),
        #                align_y=world.metres_to_pixels*(baddy.height / 2))
        #
        # diff = subtract(world, baddy_2.pos, player.pos)
        # baddy_2_ground_x = centre.x + diff.d_xy.x * world.metres_to_pixels
        # baddy_2_ground_y = centre.y + diff.d_xy.y * world.metres_to_pixels
        # draw_rectangle(SURFACE,
        #                baddy_2_ground_x, baddy_2_ground_y,
        #                world.metres_to_pixels*baddy_2.width,
        #                world.metres_to_pixels*baddy_2.height,
        #                RED,
        #                align_x=world.metres_to_pixels * (baddy_2.width / 2),
        #                align_y=world.metres_to_pixels * (baddy_2.height / 2))

        # player debug info
        if __elapsed < __debug_update_rate:
            __elapsed += delta
        else:
            __fps = 1 / delta
            __delta = delta
            __elapsed = 0

        draw_debug_text(world, 'fps : {}'.format(__fps))
        draw_debug_text(world, 'delta : {}'.format(__delta), y_offset=15)

        # draw_debug_text(world, 'd : [{}, {}]'.format(player.pos.d.x, player.pos.d.y), x_offset=player_ground_x, y_offset=player_ground_y)
        # draw_debug_text(world, 'dd : [{}, {}]'.format(dd_player_pos.x, dd_player_pos.y), x_offset=player_ground_x, y_offset=15+player_ground_y)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == '__main__':
    main()
