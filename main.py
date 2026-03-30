from algorithms.dfs import dfs
import pygame
import time
import sys
from grid.node import Node
from grid.grid import make_grid, draw_grid, get_clicked_pos
from algorithms.bfs import bfs
from algorithms.dijkstra import dijkstra
from algorithms.a_star import a_star
from algorithms.utils import reconstruct_path
from itertools import count  # needed for A* tie-breaker

pygame.init()

# Pygame setup 
WIDTH = 600
ROWS = 20
CELL_SIZE = WIDTH // ROWS
INFO_HEIGHT = 200
WIN = pygame.display.set_mode((WIDTH, WIDTH + INFO_HEIGHT))
pygame.display.set_caption("Pathfinding Visualizer")

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

# Main
def main(win):
    grid = make_grid(ROWS, CELL_SIZE)
    start = None
    end = None
    algo_gen = None
    running = False
    paused = False
    selected_algo = "BFS"
    speed = 1
    phase = "idle"

    nodes_visited = 0
    path_len = 0
    path_cost = 0
    start_time = 0
    elapsed_time = 0
    timer_started = False
    a_star_info = None
    counter = count()  # for A* tie-breaker

    clock = pygame.time.Clock()
    while True:
        clock.tick(60)

        if running and not paused:
            elapsed_time = time.time() - start_time

        draw_grid(win, grid, selected_algo, nodes_visited, path_len, path_cost,
                  elapsed_time, speed, phase, a_star_info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse input
            if pygame.mouse.get_pressed()[0]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), CELL_SIZE, WIDTH)
                if row is None: continue
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_wall()

            elif pygame.mouse.get_pressed()[2]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), CELL_SIZE, WIDTH)
                if row is None: continue
                node = grid[row][col]
                if node == start:
                    start = None
                elif node == end:
                    end = None
                node.reset()

            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not running:
                    # Reset nodes
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                            node.parent = None
                            node.distance = float('inf')
                            node.g = float('inf')
                            node.f = float('inf')
                            if(node.state != "start" and node.state != "end" and node.state != "wall"):
                                node.reset()
                    if selected_algo == "BFS":
                        algo_gen = bfs(grid, start, end)
                    elif selected_algo == "Dijkstra":
                        algo_gen = dijkstra(grid, start, end, counter)
                    elif selected_algo == "A*":
                        algo_gen = a_star(grid, start, end, counter)
                    elif selected_algo == "DFS":
                        algo_gen = dfs(grid, start, end)

                    running = True
                    paused = False
                    nodes_visited = 0
                    path_len = 0
                    start_time = 0
                    elapsed_time = 0
                    timer_started = False
                    phase = "searching"
                elif event.key == pygame.K_p and running:
                    paused = not paused
                elif event.key == pygame.K_r:
                    grid = make_grid(ROWS, CELL_SIZE)
                    start = None
                    end = None
                    algo_gen = None
                    running = False
                    paused = False
                    nodes_visited = 0
                    path_len = 0
                    start_time = 0
                    elapsed_time = 0
                    timer_started = False
                    phase = "idle"
                elif event.key == pygame.K_1:
                    selected_algo = "BFS"
                elif event.key == pygame.K_2:
                    selected_algo = "Dijkstra"
                elif event.key == pygame.K_3:
                    selected_algo = "A*"
                elif event.key == pygame.K_4:
                    selected_algo = "DFS"
                elif event.key == pygame.K_UP:
                    speed = min(speed+1, 10)
                elif event.key == pygame.K_DOWN:
                    speed = max(speed-1, 1)

        # Animation
        if running and not paused and algo_gen:
            if not timer_started:
                start_time = time.time()
                timer_started = True
            try:
                for _ in range(speed):
                    if phase == "searching":
                        action, node = next(algo_gen)

                        if action == "visit":
                            nodes_visited += 1
                        if selected_algo == "A*":
                            a_star_info = {
                                'g': getattr(node, 'g', float('inf')),
                                'h': getattr(node, 'h', float('inf')),
                                'f': getattr(node, 'f', float('inf'))
                            }
                        if node.state not in ["start", "end"]:
                            if action == "visit":
                                node.make_visited()
                            else:
                                node.make_frontier()
                                
            except StopIteration:
                if phase == "searching":
                    elapsed_time = time.time() - start_time  # Exact end time
                    if end and end.parent:
                        algo_gen = reconstruct_path(
                            end,
                            lambda: draw_grid(win, grid, selected_algo, nodes_visited, path_len, path_cost,
                                              elapsed_time, speed, "pathfinding", a_star_info)
                        )
                        phase = "pathfinding"
                        running = False  # Stop timer here

                        path_len = 0
                        path_cost = 0
                        current = end
                        while current.parent:
                            path_len += 1
                            if selected_algo == "Dijkstra" or selected_algo == "A*":
                                path_cost += current.weight
                            else:
                                path_cost += 1
                            current = current.parent
                    else:
                        phase = "unreachable"
                        running = False
                        if end:
                            end.color = ORANGE

        # Pathfinding animation (separate from timer)
        if not running and algo_gen and phase == "pathfinding":
            try:
                next(algo_gen)
            except StopIteration:
                phase = "complete"
                if selected_algo == "A*" and end:
                    a_star_info = {
                        'g': getattr(end, 'g', float('inf')),
                        'h': getattr(end, 'h', float('inf')),
                        'f': getattr(end, 'f', float('inf'))
                    }

if __name__ == "__main__":
    main(WIN)