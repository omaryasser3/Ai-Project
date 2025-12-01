def detect_cycle(node):
    # Handle empty list case
    if node is None:
        return False

    hare = tortoise = node

    while True:
        # Before moving, ensure the hare can move two steps without encountering None.
        # If hare.successor is None, the list ends (no cycle).
        # If hare.successor.successor is None, hare is at the second-to-last node,
        # and moving two steps would attempt to access 'successor' of None (the last node's successor),
        # leading to an AttributeError. In this case, the list also ends (no cycle).
        if hare.successor is None or hare.successor.successor is None:
            return False

        tortoise = tortoise.successor
        hare = hare.successor.successor

        if hare is tortoise:
            return True