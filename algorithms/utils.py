def reconstruct_path(end_node, draw):
    current = end_node
    while current.parent:
        current = current.parent
        if current.state not in ["start", "end"]:
            current.make_path()
        draw()
        yield