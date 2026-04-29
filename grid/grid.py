import pygame
from .node import Node
 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
 
def make_grid(rows, cols, cell_size):
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            node = Node(r, c, cell_size)
            row.append(node)
        grid.append(row)
    return grid

def draw_grid(win, grid, selected_algo="", nodes_visited=0, path_len=0, path_cost=0, elapsed=0, speed=1, phase="idle", a_star_info=None):
    WIDTH = win.get_width()
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win, selected_algo)
            pygame.draw.rect(win, GREY, (node.x, node.y, node.size, node.size), 1)

    pygame.draw.rect(win, WHITE, (0, WIDTH, WIDTH, WIDTH))
def get_clicked_pos(pos, cell_size, width, height):
    x, y = pos
    if y < 0 or y >= height or x < 0 or x >= width:
        return None, None
    return y // cell_size, x // cell_size