def shortest_paths(source, weight_by_edge):
    # Collect all unique nodes from the graph, including the source if it's isolated
    all_nodes = set()
    for u, v in weight_by_edge:
        all_nodes.add(u)
        all_nodes.add(v)
    all_nodes.add(source)

    # Initialize distances: infinity for all nodes, 0 for the source
    weight_by_node = {node: float('inf') for node in all_nodes}
    weight_by_node[source] = 0

    # Bellman-Ford main loop: Relax edges |V| - 1 times
    # |V| is the total number of unique nodes in the graph
    for _ in range(len(all_nodes) - 1):
        for (u, v), weight in weight_by_edge.items():
            # Only relax if the source node 'u' is reachable (its distance is not infinity)
            if weight_by_node[u] != float('inf'):
                # Relax the edge (u, v): update the distance to 'v' if a shorter path is found
                weight_by_node[v] = min(
                    weight_by_node[v],
                    weight_by_node[u] + weight
                )

    return weight_by_node