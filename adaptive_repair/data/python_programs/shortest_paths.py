def shortest_paths(source, weight_by_edge):
    # Collect all unique nodes from the graph to ensure proper initialization
    all_nodes = set()
    for u, v in weight_by_edge:
        all_nodes.add(u)
        all_nodes.add(v)
    # Ensure the source node is included, even if it has no outgoing/incoming edges
    all_nodes.add(source)

    # Initialize distances: source to itself is 0, others are infinity
    weight_by_node = {node: float('inf') for node in all_nodes}
    weight_by_node[source] = 0

    # The Bellman-Ford algorithm performs N-1 iterations, where N is the number of nodes.
    # In each iteration, it relaxes all edges.
    num_nodes = len(all_nodes)
    for i in range(num_nodes - 1):
        # Iterate over all edges in the graph
        for (u, v), weight in weight_by_edge.items():
            # Core relaxation step:
            # If a path to 'u' has been found (i.e., weight_by_node[u] is not infinity)
            # AND a path through 'u' to 'v' is shorter than the current known path to 'v',
            # then update the shortest path to 'v'.
            # The `min` function handles the `float('inf')` comparisons correctly.
            weight_by_node[v] = min(weight_by_node[v], weight_by_node[u] + weight)

    # The problem statement guarantees no negative-weight cycles, so a final check
    # for negative cycles (by running one more iteration) is not required.

    return weight_by_node