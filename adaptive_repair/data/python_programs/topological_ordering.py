import collections

def topological_ordering(nodes):
    """
    Topological Sort using Kahn's algorithm.

    Input:
        nodes: A list of directed graph nodes

    Precondition:
        The input graph is acyclic

    Output:
        A list containing the elements of nodes in an order that puts each node
        before all the nodes it has edges to.
    """
    # Calculate the initial in-degree for each node
    in_degree = {node: len(node.incoming_nodes) for node in nodes}

    # Initialize a deque (double-ended queue) with all nodes that have an in-degree of 0.
    # A deque provides O(1) append and popleft operations, which is ideal for a queue.
    q = collections.deque(node for node in nodes if in_degree[node] == 0)

    # This list will store the final ordered nodes.
    result_ordered_nodes = []

    # Process nodes from the queue
    while q:
        current_node = q.popleft()  # Get the next node from the front of the queue (O(1))
        result_ordered_nodes.append(current_node) # Add to the final result list

        # For each node that 'current_node' points to (its successor)
        for nextnode in current_node.outgoing_nodes:
            # Decrement the in-degree of the successor
            in_degree[nextnode] -= 1

            # If the in-degree of 'nextnode' becomes 0, it means all its predecessors
            # have been processed. Add 'nextnode' to the queue.
            if in_degree[nextnode] == 0:
                q.append(nextnode) # Add to the back of the queue (O(1))

    return result_ordered_nodes