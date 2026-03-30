import heapq

def dijkstra(grid, start, goal, counter=None):
    if counter is None:
        counter = iter(range(1000000))  # fallback

    start.distance = 0
    heap = [(0, next(counter), start)]
    visited = set()

    while heap:
        dist, _, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        yield ("visit", current)

        if current == goal:
            return

        for neighbor in current.neighbors:
            temp_dist = dist + getattr(neighbor, 'weight', 1)
            if temp_dist < getattr(neighbor, 'distance', float('inf')):
                neighbor.distance = temp_dist
                neighbor.parent = current
                heapq.heappush(heap, (neighbor.distance, next(counter), neighbor))
                yield ("enqueue", neighbor)