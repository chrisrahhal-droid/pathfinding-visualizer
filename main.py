from algorithms.dfs import dfs
from algorithms.gen.maze import generate_maze
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
import os, sys, socket

lock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    lock.bind('\0pathfinder_lock')
except OSError:
    sys.exit()  # already running
os.environ['SDL_VIDEO_WAYLAND_APP_ID'] = 'pathfinder'
os.environ['SDL_VIDEO_X11_WMCLASS'] = 'pathfinder'
pygame.init()
 
# Pygame setup
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

GRID_WIDTH = int(WIDTH * 0.8)
GRID_HEIGHT = int(HEIGHT * 0.8)

CELL_SIZE = 48
ROWS = GRID_HEIGHT // CELL_SIZE
COLS = GRID_WIDTH // CELL_SIZE

WIN = pygame.display.set_mode((COLS * CELL_SIZE, ROWS * CELL_SIZE))
pygame.display.set_caption("Pathfinder")
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
    grid = make_grid(ROWS, COLS, CELL_SIZE)
    start = None
    end = None
    algo_gen = None
    running = False
    paused = False
    selected_algo = "BFS"
    speed = 1
    phase = "idle"
    show_help = False
    maze_gen= None
    maze_running = False

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

        badge_font = pygame.font.SysFont("consolas", 20, bold=True)
        algo_colors = {
            "BFS":      (83, 140, 210),
            "Dijkstra": (210, 160, 83),
            "A*":       (83, 210, 140),
            "DFS":      (210, 83, 140),
        }
        badge_color = algo_colors.get(selected_algo, (150, 150, 150))
        label = badge_font.render(f"  {selected_algo}  ", True, (240, 240, 240))
        bw, bh = label.get_width() + 8, label.get_height() + 8
        bx = win.get_width() - bw - 12
        by = 12
        pygame.draw.rect(win, badge_color, (bx, by, bw, bh), border_radius=6)
        win.blit(label, (bx + 4, by + 4))

        speed_font = pygame.font.SysFont("consolas", 20, bold=True)
        speed_label = speed_font.render(f"  x{speed}  ", True, (240, 240, 240))
        tw, th = speed_label.get_width() + 8, speed_label.get_height() + 8
        tx = bx - tw - 8
        ty = by
        pygame.draw.rect(win, (60, 60, 80), (tx, ty, tw, th), border_radius=6)
        win.blit(speed_label, (tx + 4, ty + 4))

        if show_help:
            WW, WH = win.get_width(), win.get_height()

            PW = int(WW * 0.30)
            PH = int(WH * 0.55)
            PX = int(WW * 0.02)
            PY = int(WH * 0.05)

            PAD      = int(PW * 0.06)
            TITLE_H  = int(PH * 0.09)
            LINE_H   = int(PH * 0.062)
            SEC_GAP  = int(PH * 0.04)
            SMALL    = max(14, int(PH * 0.038))
            LABEL_W  = int(PW * 0.38)

            font_label  = pygame.font.SysFont("consolas", SMALL)
            font_value  = pygame.font.SysFont("consolas", SMALL)
            font_header = pygame.font.SysFont("consolas", max(11, int(SMALL * 0.78)))
            font_title  = pygame.font.SysFont("consolas", int(SMALL * 1.1), bold=True)

            # Background
            bg = pygame.Surface((PW, PH), pygame.SRCALPHA)
            bg.fill((15, 15, 20, 245))
            win.blit(bg, (PX, PY))

            # Outer border
            pygame.draw.rect(win, (80, 80, 100), (PX, PY, PW, PH), 1, border_radius=6)

            # Title bar
            title_bar = pygame.Surface((PW, TITLE_H), pygame.SRCALPHA)
            title_bar.fill((60, 52, 137, 220))
            win.blit(title_bar, (PX, PY))
            pygame.draw.line(win, (100, 90, 180), (PX, PY + TITLE_H), (PX + PW, PY + TITLE_H), 1)

            t = font_title.render("HELP", True, (206, 203, 246))
            win.blit(t, (PX + PAD, PY + (TITLE_H - t.get_height()) // 2))
            hint = font_header.render("H to close", True, (120, 110, 180))
            win.blit(hint, (PX + PW - hint.get_width() - PAD, PY + (TITLE_H - hint.get_height()) // 2))

            controls = [
                ("Left click",   "Place start/end/walls"),
                ("Right click",  "Erase node"),
                ("Space",        "Run algorithm"),
                ("P",            "Pause / Resume"),
                ("R",            "Reset grid"),
                ("G",           "Generate maze"),
                ("UP / DOWN",    "Change speed"),
            ]
            algorithms = [
                ("1", "BFS"),
                ("2", "Dijkstra"),
                ("3", "A*"),
                ("4", "DFS"),
            ]

            def draw_section_header(text, cy):
                s = font_header.render(text.upper(), True, (100, 140, 200))
                win.blit(s, (PX + PAD, cy))
                line_y = cy + s.get_height() + 3
                pygame.draw.line(win, (40, 50, 70), (PX + PAD, line_y), (PX + PW - PAD, line_y), 1)
                return line_y + int(LINE_H * 0.4)

            cy = PY + TITLE_H + SEC_GAP

            cy = draw_section_header("Controls", cy)
            for key, desc in controls:
                k = font_label.render(key, True, (120, 120, 140))
                v = font_value.render(desc, True, (210, 210, 210))
                win.blit(k, (PX + PAD, cy))
                win.blit(v, (PX + PAD + LABEL_W, cy))
                cy += LINE_H

            cy += SEC_GAP
            cy = draw_section_header("Algorithms", cy)

            col_w = (PW - PAD * 2) // 2
            for i, (key, name) in enumerate(algorithms):
                col_x = PX + PAD + (i % 2) * col_w
                row_y = cy + (i // 2) * LINE_H

                badge = pygame.Surface((int(SMALL * 1.4), int(SMALL * 1.4)), pygame.SRCALPHA)
                badge.fill((83, 74, 183, 130))
                win.blit(badge, (col_x, row_y))
                bk = font_label.render(key, True, (206, 203, 246))
                win.blit(bk, (col_x + (badge.get_width() - bk.get_width()) // 2,
                            row_y + (badge.get_height() - bk.get_height()) // 2))
                n = font_value.render(name, True, (210, 210, 210))
                win.blit(n, (col_x + badge.get_width() + 8, row_y + (badge.get_height() - n.get_height()) // 2))
     
        if phase in ("complete", "unreachable"):
            WW, WH = win.get_width(), win.get_height()

            PW = int(WW * 0.16)
            PH = int(WH * 0.32)
            PX = WW - PW - int(WW * 0.02)
            PY = int(WH * 0.05)

            PAD    = int(PW * 0.08)
            TITLE_H = int(PH * 0.14)
            LINE_H  = int((PH - TITLE_H) / 5.5)
            SMALL   = max(12, int(PH * 0.058))

            font_label = pygame.font.SysFont("consolas", SMALL)
            font_value = pygame.font.SysFont("consolas", SMALL, bold=True)
            font_title = pygame.font.SysFont("consolas", int(SMALL * 1.05), bold=True)

            # Background
            bg = pygame.Surface((PW, PH), pygame.SRCALPHA)
            bg.fill((15, 15, 20, 245))
            win.blit(bg, (PX, PY))

            # Border
            pygame.draw.rect(win, (60, 100, 80), (PX, PY, PW, PH), 1, border_radius=6)

            # Title bar — green if complete, orange if unreachable
            bar_color = (15, 80, 65, 220) if phase == "complete" else (100, 50, 10, 220)
            title_bar = pygame.Surface((PW, TITLE_H), pygame.SRCALPHA)
            title_bar.fill(bar_color)
            win.blit(title_bar, (PX, PY))
            pygame.draw.line(win, (60, 150, 110), (PX, PY + TITLE_H), (PX + PW, PY + TITLE_H), 1)

            t = font_title.render("RESULTS", True, (159, 225, 203))
            win.blit(t, (PX + PAD, PY + (TITLE_H - t.get_height()) // 2))

            algo_hint = font_label.render(ran_algo, True, (100, 160, 130))
            win.blit(algo_hint, (PX + PW - algo_hint.get_width() - PAD,
                                PY + (TITLE_H - algo_hint.get_height()) // 2))

            # Rows
            if phase == "complete":
                rows = [
                    ("Phase",         "complete"),
                    ("Nodes visited", str(nodes_visited)),
                    ("Path steps",    str(path_len)),
                    ("Path cost",     str(path_cost)),
                    ("Time",          f"{elapsed_time:.2f}s"),
                ]
            elif phase == "unreachable":
                rows = [
                    ("Phase",         "unreachable"),
                    ("Nodes visited", str(nodes_visited)),
                    ("Path steps",    "—"),
                    ("Path cost",     "—"),
                    ("Time",          f"{elapsed_time:.2f}s"),
                ]

            cy = PY + TITLE_H + int(LINE_H * 0.4)
            for i, (label, value) in enumerate(rows):
                lbl = font_label.render(label, True, (120, 120, 140))
                val = font_value.render(value, True, (210, 210, 210))
                win.blit(lbl, (PX + PAD, cy))
                win.blit(val, (PX + PW - val.get_width() - PAD, cy))

                if i < len(rows) - 1:
                    div_y = cy + LINE_H - int(LINE_H * 0.15)
                    pygame.draw.line(win, (35, 45, 40),
                                    (PX + PAD, div_y), (PX + PW - PAD, div_y), 1)
                cy += LINE_H
       

        if not show_help:
            win.blit(pygame.font.SysFont("monospace", 28).render("Press H for help", True, (150, 150, 150)), (10, win.get_height() - 40))

        if paused:
            surf = win.copy()

            scale = 0.15
            w, h = surf.get_size()

            surf = pygame.transform.smoothscale(surf, (int(w*scale), int(h*scale)))
            surf = pygame.transform.smoothscale(surf, (w, h))

            win.blit(surf, (0, 0))

            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            win.blit(overlay, (0, 0))

            font = pygame.font.SysFont("consolas", 50, bold=True)
            text = font.render("PAUSED", True, (255, 255, 255))
            win.blit(text, (w//2 - text.get_width()//2, h//2))
        pygame.display.flip()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
         
                # Mouse input
            if phase in ("idle", "complete", "unreachable"):
                if pygame.mouse.get_pressed()[0]:
                    row, col = get_clicked_pos(pygame.mouse.get_pos(), CELL_SIZE, WIDTH, HEIGHT)
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
                    row, col = get_clicked_pos(pygame.mouse.get_pos(), CELL_SIZE, WIDTH, HEIGHT)
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
                                node.resetwithoutweight()
                            if(node.state == "end"):
                                node.make_end()
                    if selected_algo == "BFS":
                        algo_gen = bfs(grid, start, end)
                    elif selected_algo == "Dijkstra":
                        algo_gen = dijkstra(grid, start, end, counter)
                    elif selected_algo == "A*":
                        algo_gen = a_star(grid, start, end, counter)
                    elif selected_algo == "DFS":
                        algo_gen = dfs(grid, start, end)
                    ran_algo = selected_algo
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
                    grid = make_grid(ROWS, COLS, CELL_SIZE)
                    start = None
                    end = None
                    algo_gen = None
                    running = False
                    paused = False
                    maze_gen = None
                    maze_running = False
                    nodes_visited = 0
                    path_len = 0
                    start_time = 0
                    elapsed_time = 0
                    timer_started = False
                    phase = "idle"
                elif event.key == pygame.K_h:
                        show_help = not show_help
                allowed_phases = {"idle", "complete", "unreachable"}
                if phase in allowed_phases:
                    if event.key == pygame.K_1:
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
                    elif event.key == pygame.K_g :
                        # reset all non-start/end nodes before carving
                       # 1. clear everything
                       if not maze_running:
                            phase = "idle"
                            for row in grid:
                                for node in row:
                                    node.reset()

                            start = None
                            end = None

                            # 2. generate maze
                            maze_gen = generate_maze(grid, ROWS, COLS)
                            maze_running = True
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
        if not running and maze_running and maze_gen:
            try:
                for _ in range(speed * 4):
                    next(maze_gen)
            except StopIteration:
                maze_running = False
                maze_gen     = None
             # Collect all carved (passable) interior cells
                carved = [
                    grid[r][c]
                    for r in range(1, ROWS - 1)
                    for c in range(1, COLS - 1)
                    if grid[r][c].state == "empty"
                ]

                if not start and not end:
                    # Pick two random cells, ensure they're far apart
                    import random
                    random.shuffle(carved)
                    half = len(carved) // 2
                    start = carved[0]
                    # pick end from the second half so they're distant
                    end = carved[half + random.randint(0, half - 1)]
                    start.make_start()
                    end.make_end()

                elif not start:
                    candidates = [n for n in carved if n != end]
                    start = random.choice(candidates)
                    start.make_start()

                elif not end:
                    candidates = [n for n in carved if n != start]
                    end = random.choice(candidates)
                    end.make_end()
                # if both already exist → do nothing, keep them
 
if __name__ == "__main__":
    main(WIN)
