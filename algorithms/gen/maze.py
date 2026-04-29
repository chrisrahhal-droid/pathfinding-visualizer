import random

def generate_maze(grid, rows, cols):
   # Step 1: fill all cells with walls (border stays walls permanently,
#         interior gets carved by the backtracker)
    for r in range(0, rows ):
        for c in range(0, cols ):
            if grid[r][c].state not in ("start", "end"):
                grid[r][c].make_wall()

    # Step 2: recursive backtracker on "room" cells (odd indices)
    # rooms are at r=1,3,5... c=1,3,5... — even cells between them are walls
    visited = set()
    visited.add((1, 1))

    if grid[1][1].state not in ("start", "end"):
        grid[1][1].reset()
        yield ('carve', grid[1][1])

    stack = [(1, 1)]

    while stack:
        r, c = stack[-1]

        neighbors = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = r + dr, c + dc
            if 1 <= nr <= rows - 1 and 1 <= nc <= cols - 1 and (nr, nc) not in visited:
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            nr, nc, dr, dc = random.choice(neighbors)
            visited.add((nr, nc))

            # carve the wall between current room and chosen neighbor
            wr, wc = r + dr // 2, c + dc // 2
            if grid[wr][wc].state not in ("start", "end"):
                grid[wr][wc].reset()
                yield ('carve', grid[wr][wc])

            if grid[nr][nc].state not in ("start", "end"):
                grid[nr][nc].reset()
                yield ('carve', grid[nr][nc])

            stack.append((nr, nc))
        else:
            stack.pop()
            