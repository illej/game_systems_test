import collections
import heapq
from copy import deepcopy


class SimpleGraph(object):
    def __init__(self):
        self.edges = {}

    def neighbours(self, id):
        return self.edges[id]


class SquareGrid(object):
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.walls = []

    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def is_passable(self, id):
        return id not in self.walls

    def neighbours(self, id):
        (x, y) = id
        results = [(x+1, y),
                   (x, y-1),
                   (x-1, y),
                   (x, y+1)]

        if (x + y) % 2 == 0:
            results.reverse()

        results = filter(self.in_bounds, results)
        results = filter(self.is_passable, results)

        return results


class WeightedGrid(SquareGrid):
    def __init__(self, w, h):
        super().__init__(w, h)
        self.weights = {}

    def cost(self, from_node, to_node):
        return self.weights.get(to_node, 1)


class Queue(object):
    def __init__(self):
        self.elements = collections.deque()

    def is_empty(self):
        return len(self.elements) == 0

    def add(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


class PriorityQueue(object):
    def __init__(self):
        self.elements = []

    def is_empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class MovementComponent(object):
    # TODO: move the pathfinding stuff to a component
    def __init__(self):
        self.path = []
        self.step_i = 0
        self.target = None

    def heuristic(self, a, b):
        """
        >>> m = MovementComponent()
        >>> m.heuristic((0, 0), (4, 2))
        6
        >>> m.heuristic((0, 0), (4, 0))
        4
        >>> m.heuristic((0, 1), (4, 0))
        5
        """
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def a_star_search(self, grid, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)

        came_from = dict()
        cost_so_far = dict()

        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.is_empty():
            current = frontier.get()

            if current == goal:
                break

            for next in grid.neighbours(current):
                new_cost = cost_so_far[current] + grid.cost(current, next)

                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far

    def reconstruct_path(self, came_from, start, goal):
        current = goal

        while current != start:
            self.path.append(current)
            current = came_from[current]

        # self.path.append(start)
        self.path.reverse()

        return self.path

    def get_path(self, world, tile_map, start, goal):
        count_x = 34
        count_y = 18
        grid = WeightedGrid(count_x, count_y)

        for y in range(count_y):
            for x in range(count_x):
                if tile_map.tiles[y][x] == 1:
                    grid.walls.append((x, y))

        came_from, cost_so_far = self.a_star_search(grid, start, goal)
        path = self.reconstruct_path(came_from, start, goal)

        return path

    def move(self, func, world, actor, step, delta_time):
        if step != (actor.pos.tile_x, actor.pos.tile_y):
            step_x, step_y = step

            x_delta = step_x - actor.pos.tile_x
            y_delta = step_y - actor.pos.tile_y

            # speed
            x_delta *= 5
            y_delta *= 5

            new_pos = deepcopy(actor.pos)
            new_pos.x += (delta_time * x_delta)
            new_pos.y += (delta_time * y_delta)
            new_pos = func(world, new_pos)

            actor.pos = deepcopy(new_pos)

            return False
        return True

    def need_new_path(self, start, goal):
        result = False

        if 0 < self.heuristic(start, goal) < 7:
            if len(self.path) == 0 or self.target != goal:
                result = True

        return result

    def update(self, func, world, tile_map, actor, target, delta_time):
        start = (actor.pos.abs_tile_x, actor.pos.abs_tile_y)
        goal = (target.pos.abs_tile_x, target.pos.abs_tile_y)

        if not self.target:
            self.target = goal

        if self.need_new_path(start, goal):
            self.path = []
            self.path = self.get_path(world, tile_map, start, goal)
            self.step_i = 0
            self.target = goal
        else:
            if self.step_i < len(self.path):
                step = self.path[self.step_i]

                if self.move(func, world, actor, step, delta_time):
                    self.step_i += 1


if __name__ == '__main__':
    grid = [
        [2, 1, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 3],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0]
    ]
    grid_width = len(grid[0])
    grid_height = len(grid)

    w_grid = WeightedGrid(grid_width, grid_height)

    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] == 1:
                w_grid.walls.append((x, y))

    print('walls:', w_grid.walls)

    mov = MovementComponent()

    start = (0, 0)
    goal = (4, 2)
    path = []
    if mov.heuristic(start, goal) < 5:
        came_from, cost_so_far = mov.a_star_search(w_grid, start, goal)
        path = mov.reconstruct_path(came_from, start, goal)

        print('came_from:', came_from)
        print('cost_so_far:', cost_so_far)
    print('path:', path)

    for y in range(grid_height):
        row = ''
        for x in range(grid_width):
            tile = grid[y][x]
            if (x, y) in path:
                tile = 'x'
            row += str(tile) + ' '
        print(row)
    #
    # import doctest
    # doctest.testmod(verbose=True)

