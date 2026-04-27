def dfs(grid, start, goal):
    stack = [start]
    visited = {start}

    while stack:
        current = stack.pop()
        yield ("visit", current)

        if current == goal:
            return

        for neighbor in current.neighbors:
            if neighbor not in visited:
                neighbor.parent = current
                stack.append(neighbor)
                visited.add(neighbor)
                yield ("enqueue", neighbor)