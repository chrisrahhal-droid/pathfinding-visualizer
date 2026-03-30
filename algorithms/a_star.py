import heapq
from itertools import count

def heuristic(a, b):
    # Manhattan distance
    return abs(a.row - b.row) + abs(a.col - b.col)

def a_star(grid, start, goal, counter=None):
    if counter is None:
        counter = count()

    start.g = 0
    start.h = heuristic(start, goal)
    start.f = start.h
    heap = [(start.f, next(counter), start)]
    visited = set()

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        yield ("visit", current)

        if current == goal:
            return

        for neighbor in current.neighbors:
            tentative_g = current.g + getattr(neighbor, "weight", 1)  
            if tentative_g < getattr(neighbor, "g", float('inf')):
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, goal)
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current
                heapq.heappush(heap, (neighbor.f, next(counter), neighbor))
                yield ("enqueue", neighbor)