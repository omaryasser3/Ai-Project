from collections import deque as Queue

def breadth_first_search(startnode, goalnode):
    queue = Queue()
    queue.append(startnode)

    nodesseen = set()
    nodesseen.add(startnode)

    while queue:  # This correctly checks if the queue is not empty
        node = queue.popleft()

        if node is goalnode:
            return True
        else:
            # Filter successors to add only those not yet seen
            new_successors = [s for s in node.successors if s not in nodesseen]
            queue.extend(new_successors)
            # Add the newly discovered successors to the set of seen nodes
            nodesseen.update(new_successors)

    return False