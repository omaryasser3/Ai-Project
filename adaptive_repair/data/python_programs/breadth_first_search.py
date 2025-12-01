from collections import deque as Queue

def breadth_first_search(startnode, goalnode):
    queue = Queue()
    queue.append(startnode)

    nodesseen = set()
    nodesseen.add(startnode)

    while queue:  # Loop as long as there are nodes in the queue to process
        node = queue.popleft()

        if node is goalnode:
            return True
        else:
            # Only add successors to the queue if they haven't been seen yet
            # and mark them as seen immediately upon adding to the queue.
            for successor_node in node.successors:
                if successor_node not in nodesseen:
                    queue.append(successor_node)
                    nodesseen.add(successor_node)

    return False # If the queue becomes empty and goalnode was not found, it's unreachable
