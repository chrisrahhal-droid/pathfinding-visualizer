import pygame
import random

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (200, 200, 200)

WEIGHT_FONT = None

def get_weight_font():
    global WEIGHT_FONT
    if WEIGHT_FONT is None:
        WEIGHT_FONT = pygame.font.SysFont('Arial', 12)
    return WEIGHT_FONT

def get_weight_color(weight):
    if weight == 0 or weight == float('inf'):
        return WHITE if weight == 0 else BLACK
    shade = 255 - (weight - 1) * 25  
    return (shade, shade, shade)

class Node:
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.size = size
        self.x = col * size
        self.y = row * size

        self.color = WHITE
        self.state = "empty"
        self.neighbors = []
        self.parent = None

        # For Dijkstra / A*
        self.distance = float('inf')
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')
        self.weight = random.randint(1, 10)  # Random weight for Dijkstra

    def draw(self, win, selected_algo):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))
        
        if selected_algo in ["Dijkstra", "A*"] and self.state != "wall":
            weight_text = str(self.weight) if self.weight != float('inf') else '∞'
            font = get_weight_font()
            text_color = BLACK if self.state in ["empty", "start", "end"] else WHITE
            text_surf = font.render(weight_text, True, text_color)  # True is for antialiasing
            text_rect = text_surf.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
            win.blit(text_surf, text_rect)

    def make_wall(self):
        self.color = BLACK
        self.state = "wall"
        self.weight = float('inf')

    def make_start(self):
        self.color = GREEN
        self.state = "start"
        self.weight = 0  

    def make_end(self):
        self.color = RED
        self.state = "end"
        self.weight = 0  

    def reset(self):
        self.color = WHITE
        self.state = "empty"
    
    def generate_weight(self):
        self.weight = random.randint(1, 10)  # Reset to random weight

    def is_wall(self):
        return self.state == "wall"

    def make_visited(self):
        self.color = BLUE
        self.state = "visited"

    def make_frontier(self):
        self.color = YELLOW
        self.state = "frontier"

    def make_path(self):
        self.color = PURPLE
        self.state = "path"

    def make_weighted(self, weight):
        self.weight = weight
        self.color = ORANGE if weight > 1 else WHITE
        self.state = "weighted" if weight > 1 else "empty"

    def update_neighbors(self, grid):
        self.neighbors = []
        rows = len(grid)
        cols = len(grid[0])
        if self.row > 0 and not grid[self.row-1][self.col].is_wall():
            self.neighbors.append(grid[self.row-1][self.col])
        if self.row < rows - 1 and not grid[self.row+1][self.col].is_wall():
            self.neighbors.append(grid[self.row+1][self.col])
        if self.col > 0 and not grid[self.row][self.col-1].is_wall():
            self.neighbors.append(grid[self.row][self.col-1])
        if self.col < cols - 1 and not grid[self.row][self.col+1].is_wall():
            self.neighbors.append(grid[self.row][self.col+1])