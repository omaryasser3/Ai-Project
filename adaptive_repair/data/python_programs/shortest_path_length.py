from heapq import *

def shortest_path_length(length_by_edge, startnode, goalnode):
    # distances[node] stores the shortest distance found so far from startnode to node.
    # Initialize startnode's distance to 0, others are implicitly infinity.
    distances = {startnode: 0}
    
    # priority_queue is a min-heap storing (distance, node) tuples.
    # It allows for efficient retrieval of the node with the smallest distance.
    priority_queue = [(0, startnode)]
    
    # finalized_nodes stores nodes for which the shortest path has been definitively determined.
    finalized_nodes = set()

    while priority_queue:
        current_dist, current_node = heappop(priority_queue)

        # Optimization/Correction: Implement robust lazy deletion.
        # If the distance of the popped entry (`current_dist`) is greater than the
        # currently known shortest distance to `current_node` (stored in `distances`),
        # it means this entry is outdated (a shorter path has already been found and processed).
        # We skip such outdated entries to ensure correctness and efficiency.
        if current_dist > distances[current_node]:
            continue

        # If this node has already been finalized (i.e., its shortest path has been
        # definitively determined and its neighbors processed), skip this entry.
        # This prevents redundant work and is a core part of Dijkstra's algorithm.
        if current_node in finalized_nodes:
            continue

        # If we've reached the goal node, we've found the shortest path.
        if current_node is goalnode:
            return current_dist

        # Mark the current node as finalized; its shortest path is now known.
        finalized_nodes.add(current_node)

        # Explore all neighbors (successors) of the current node.
        for nextnode in current_node.successors:
            # If the neighbor's shortest path has already been finalized, skip it.
            if nextnode in finalized_nodes:
                continue

            # Calculate the distance to the neighbor through the current_node.
            # Use .get() with float('inf') as default for robustness if an edge is missing.
            edge_length = length_by_edge.get((current_node, nextnode), float('inf'))
            new_dist = current_dist + edge_length

            # If this new path to nextnode is shorter than any previously known path,
            # update its distance in the 'distances' dictionary and add it to the priority queue.
            # We use distances.get(nextnode, float('inf')) to handle nodes not yet in distances.
            if new_dist < distances.get(nextnode, float('inf')):
                distances[nextnode] = new_dist
                heappush(priority_queue, (new_dist, nextnode))

    # If the loop finishes and the goal node was not reached, it's unreachable.
    return float('inf')