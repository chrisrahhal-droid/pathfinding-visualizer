from collections import deque

def bfs(grid, start, goal):
    queue = deque()
    queue.append(start)
    visited = {start}

    while queue:
        current = queue.popleft()
        yield ("visit", current)

        if current == goal:
            return

        for neighbor in current.neighbors:
            if neighbor not in visited:
                neighbor.parent = current
                queue.append(neighbor)
                visited.add(neighbor)
                yield ("enqueue", neighbor)