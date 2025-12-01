import collections

def topological_ordering(nodes):
    # 1. Calculate the in-degree for each node.
    # The in-degree is the number of incoming edges to a node.
    # This is a crucial step for Kahn's algorithm to track dependencies.
    in_degree = {node: len(node.incoming_nodes) for node in nodes}

    # 2. Initialize a queue with all nodes that have an in-degree of 0.
    # These are the nodes that have no prerequisites and can be processed first.
    # Optimization: Use collections.deque for efficient O(1) popleft operations.
    queue = collections.deque([node for node in nodes if in_degree[node] == 0])

    # 3. Initialize the list that will store the topologically sorted nodes.
    ordered_nodes = []

    # 4. Process nodes from the queue until it's empty.
    while queue:
        # Dequeue a node. This node has all its prerequisites met.
        # Optimization: Use deque.popleft() for O(1) removal from the front.
        current_node = queue.popleft()
        ordered_nodes.append(current_node)

        # For each neighbor (node that 'current_node' points to):
        for neighbor in current_node.outgoing_nodes:
            # Decrement the neighbor's in-degree.
            # This signifies that one of its prerequisites (current_node) has been processed.
            in_degree[neighbor] -= 1

            # If the neighbor's in-degree becomes 0, it means all its prerequisites
            # have now been processed. So, it can be added to the queue.
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # The problem statement guarantees the graph is acyclic.
    # If it were not, len(ordered_nodes) would be less than len(nodes),
    # indicating a cycle.
    # if len(ordered_nodes) != len(nodes):
    #     raise ValueError("Graph contains a cycle, topological sort is not possible.")

    return ordered_nodes
