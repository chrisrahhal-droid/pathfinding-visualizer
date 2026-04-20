import pygame
from .node import Node
 
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
 
# Grid functions
def make_grid(rows, size):
    grid = []
    for r in range(rows):
        row = []
        for c in range(rows):
            node = Node(r, c, size)
            row.append(node)
        grid.append(row)
    return grid
 
def draw_grid(win, grid, INFO_HEIGHT, selected_algo="", nodes_visited=0, path_len=0, path_cost=0, elapsed=0, speed=1, phase="idle", a_star_info=None):
    FONT = pygame.font.SysFont('Arial', 18)
    INFO_HEIGHT = 200
    WIDTH = win.get_width()  
 
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win, selected_algo)
            pygame.draw.rect(win, GREY, (node.x, node.y, node.size, node.size), 1)
 
    info_y = WIDTH
    # pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(win, WHITE, (0, info_y, WIDTH, INFO_HEIGHT))
    # pygame.draw.line(surface, color, start_pos, end_pos, width)
    pygame.draw.line(win, BLACK, (0, info_y), (WIDTH, info_y), 2)
 
    texts = [
        f"Algorithm: {selected_algo}",
        f"Phase: {phase}",
        f"Nodes visited: {nodes_visited}",
        f"Path length (steps): {path_len}",
        f"Path cost: {path_cost}",
        f"Time: {elapsed:.3f}s",
        f"Speed: {speed} (UP/DOWN to change)",
        "Controls: LEFT click = wall/start/end, RIGHT click = erase",
        "SPACE = start, P = pause/resume, R = reset, 1=BFS 2=Dijkstra 3=A* 4=DFS"
    ]
    line_height = 20
    for i, t in enumerate(texts):
        y_pos = info_y + 5 + i*line_height
        txt_surf = FONT.render(t, True, BLACK)
        win.blit(txt_surf, (5, y_pos))
        pygame.draw.line(win, (180,180,180), (0, y_pos+line_height), (WIDTH, y_pos+line_height), 1)
 
    pygame.draw.line(win, BLACK, (0, info_y+INFO_HEIGHT-2), (WIDTH, info_y+INFO_HEIGHT-2), 2)
    # Pushes all your drawings (grid + panel + text + lines) to the actual window.
    pygame.display.update()
 
def get_clicked_pos(pos, cell_size, width):
    x, y = pos
    if y < 0 or y >= width or x < 0 or x >= width:
        return None, None
    return y // cell_size, x // cell_size