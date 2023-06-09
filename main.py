import time
import threading
import pygame as pg
import math
import queue as q
import sys

sys.setrecursionlimit(100000)

WIDTH = 600

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
CYAN = 0, 255, 255
PURPLE = 255, 0, 255
GREY = 128, 128, 128

WINDOW = pg.display.set_mode((WIDTH, WIDTH))


class Node:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.width = width
        self.color = WHITE
        self.parent = None

        self.neighbours = []

        self.x = col * self.width
        self.y = row * self.width

    def get_position(self): return self.row, self.col

    def get_coordinates(self): return self.y, self.x

    def is_open(self): return self.color == WHITE

    def is_closed(self): return self.color == RED

    def is_start(self): return self.color == YELLOW

    def is_end(self): return self.color == CYAN

    def is_barrier(self): return self.color == BLACK

    def is_path(self): return self.color == PURPLE

    def is_next(self): return self.color == GREEN

    def set_closed(self): self.color = RED

    def set_start(self): self.color = YELLOW

    def set_end(self): self.color = CYAN

    def set_barrier(self): self.color = BLACK

    def set_path(self): self.color = PURPLE

    def set_next(self): self.color = GREEN

    def reset(self): self.color = WHITE

    def draw(self): pg.draw.rect(WINDOW, self.color, pg.Rect(self.x, self.y, self.width, self.width))


def set_neighbours(grid: list[list[Node]]):
    for row in grid:
        for node in row:
            if node.is_open():
                y, x = node.get_position()
                if y > 0 and grid[y - 1][x].is_open():
                    grid[y][x].neighbours.append(grid[y - 1][x])
                if x > 0 and grid[y][x - 1].is_open():
                    grid[y][x].neighbours.append(grid[y][x - 1])
                if y < len(grid) - 1 and grid[y + 1][x].is_open():
                    grid[y][x].neighbours.append(grid[y + 1][x])
                if x < len(grid) - 1 and grid[y][x + 1].is_open():
                    grid[y][x].neighbours.append(grid[y][x + 1])


def reset(grid: list[list[Node]]):
    for y, row in enumerate(grid):
        if y == 0 or y == len(grid) - 1: continue
        for x, val in enumerate(row):
            if x == 0 or x == len(grid) - 1: continue
            grid[y][x].reset()


def build_grid(rows):
    grid = [[] for _ in range(rows)]
    for y in range(rows):
        for x in range(rows):
            node = Node(y, x, WIDTH // rows)
            if y == 0 or x == 0 or y == rows - 1 or x == rows - 1: node.set_barrier()
            grid[y].append(node)
    return grid


def draw_grid(grid):
    for row in grid:
        for node in row:
            node.draw()
    n = len(grid)
    gap = grid[0][0].width
    for i in range(n):
        pg.draw.line(WINDOW, GREY, (0, i * gap), (WIDTH, i * gap))
        pg.draw.line(WINDOW, GREY, (i * gap, 0), (i * gap, WIDTH))


def draw(grid):
    WINDOW.fill(WHITE)
    draw_grid(grid)
    pg.display.update()


def get_grid_pos(mouse_x, mouse_y, width):
    return mouse_y // width, mouse_x // width


def bfs(grid: list[list[Node]], start: Node, end: Node):
    Q = q.Queue()
    Q.put(start)
    found = False
    end_y, end_x = end.get_position()

    while not Q.empty():
        node: Node = Q.get()
        for neighbour in node.neighbours:
            if neighbour.is_open() or neighbour.is_next():
                y, x = neighbour.get_position()
                grid[y][x].set_closed()
                time.sleep(0.01)
                grid[y][x].parent = node
                Q.put(grid[y][x])
                for other in neighbour.neighbours:
                    if other.is_open():
                        y, x = other.get_position()
                        grid[y][x].set_next()
            if neighbour.is_end():
                found = True
                grid[end_y][end_x].parent = node
                break

        if found:
            end = end.parent
            while end.parent is not None:
                y, x = end.get_position()
                grid[y][x].set_path()
                end = end.parent

            break


def dfs(grid: list[list[Node]], start: Node, end: Node):
    found = False

    def visit(v: Node):
        nonlocal found
        nonlocal end
        if found: return
        for u in v.neighbours:
            if found: break
            if u.is_open() or u.is_next():
                time.sleep(0.01)
                y, x = u.get_position()
                grid[y][x].set_closed()
                grid[y][x].parent = v
                for k in u.neighbours:
                    if k.is_open():
                        py, px = k.get_position()
                        grid[py][px].set_next()
                visit(grid[y][x])
            elif u.is_end():
                y, x = u.get_position()
                grid[y][x].parent = v
                found = True
                while end.parent is not None:
                    y, x = end.get_position()
                    grid[y][x].set_path()
                    end = end.parent
                break
        if found:
            return

    visit(start)


def h(node1: Node, node2: Node):
    y1, x1 = node1.get_position()
    y2, x2 = node2.get_position()
    return abs(y1 - y2) + abs(x1 - x2)


def a_star(grid, start, end):
    Q = q.PriorityQueue()
    count = 0
    g = {node: math.inf for row in grid for node in row}
    g[start] = 0
    f = {node: math.inf for row in grid for node in row}
    f[start] = h(start, end)
    open_set = {start}
    Q.put((0, count, start))
    found = False

    while not Q.empty():
        f_score, c, node = Q.get()
        open_set.remove(node)
        for v in node.neighbours:
            y, x = v.get_position()
            if (v.is_open() or v.is_next()) and g[v] > g[node] + 1:
                g[v] = g[node] + 1
                f[v] = g[v] + h(v, end)
                if v not in open_set:
                    count += 1
                    grid[y][x].parent = node
                    time.sleep(0.001)
                    Q.put((f[v], count, grid[y][x]))
                    open_set.add(grid[y][x])
                    grid[y][x].set_next()

            if v.is_end():
                end.parent = node
                found = True
                current = end
                while not current.is_start():
                    y, x = current.get_position()
                    grid[y][x].set_path()
                    current = current.parent
                y, x = end.get_position()
                grid[y][x].set_end()
                y, x = start.get_position()
                grid[y][x].set_start()

                break
        if found: break
        y, x = node.get_position()
        if node != start:
            grid[y][x].set_closed()


def main():
    ROWS = 40
    grid: list[list[Node]] = build_grid(ROWS)
    run = True
    start, end = None, None

    set_neighbours(grid)

    while run:
        press = pg.mouse.get_pressed()
        if press[0]:
            pos = pg.mouse.get_pos()
            pos = get_grid_pos(pos[0], pos[1], WIDTH // ROWS)
            y, x = pos
            if 0 <= y < ROWS and 0 <= x < ROWS:
                if start is None and grid[y][x].is_open():
                    start = grid[y][x]
                    grid[y][x].set_start()
                elif end is None and grid[y][x].is_open():
                    end = grid[y][x]
                    grid[y][x].set_end()
                elif grid[y][x].is_open():
                    grid[y][x].set_barrier()
        elif press[2]:
            pos = pg.mouse.get_pos()
            pos = get_grid_pos(pos[0], pos[1], WIDTH // ROWS)
            y, x = pos
            if 0 < y < ROWS - 1 and 0 < x < ROWS - 1:
                if grid[y][x].is_start():
                    start = None
                elif grid[y][x].is_end():
                    end = None
                grid[y][x].reset()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_b:
                    if start is not None and end is not None:
                        BFS = threading.Thread(target=lambda: bfs(grid, start, end),
                                               daemon=True)
                        BFS.start()
                if event.key == pg.K_d:
                    if start is None or end is None:
                        continue
                    DFS = threading.Thread(target=lambda: dfs(grid, start, end),
                                           daemon=True)
                    DFS.start()
                if event.key == pg.K_a:
                    if start is None or end is None: continue
                    ASTAR = threading.Thread(target=lambda: a_star(grid, start, end), daemon=True)
                    ASTAR.start()
                if event.key == pg.K_r:
                    reset(grid)
                    start = None
                    end = None

        draw(grid)

    pg.quit()


if __name__ == '__main__':
    main()
