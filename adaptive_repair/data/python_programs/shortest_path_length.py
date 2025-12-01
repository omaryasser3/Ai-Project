from heapq import *

def shortest_path_length(length_by_edge, startnode, goalnode):
    unvisited_nodes = [] # Min-heap containing (distance, node) pairs
    heappush(unvisited_nodes, (0, startnode))
    visited_nodes = set()

    while len(unvisited_nodes) > 0:
        distance, node = heappop(unvisited_nodes)
        
        # If we've already finalized the shortest path to this node, skip.
        # This handles cases where a node might be pushed multiple times with different distances
        # before its shortest path is finalized.
        if node in visited_nodes:
            continue

        if node is goalnode:
            return distance

        visited_nodes.add(node)

        for nextnode in node.successors:
            # If the successor node has already been visited and its shortest path finalized,
            # we don't need to process it again.
            if nextnode in visited_nodes:
                continue

            # Calculate the new distance to nextnode via the current node
            new_dist_via_current_node = distance + length_by_edge[node, nextnode]

            # Get the current known distance to nextnode from the heap.
            # If not found, it's treated as infinity.
            current_dist_to_nextnode = get(unvisited_nodes, nextnode)

            # If the new path is shorter, update or insert it into the priority queue.
            if new_dist_via_current_node < current_dist_to_nextnode:
                insert_or_update(unvisited_nodes, (new_dist_via_current_node, nextnode))

    return float('inf')


def get(node_heap, wanted_node):
    """Retrieves the current distance of a node from the heap. Returns infinity if not found."""
    for dist, node in node_heap:
        if node == wanted_node:
            return dist
    return float('inf') # BUG FIX: Changed from 0 to float('inf')

def insert_or_update(node_heap, dist_node):
    """Inserts a new (distance, node) pair or updates an existing one in the heap.
       If updating, it removes the old entry and adds the new one to maintain heap property."""
    dist, node = dist_node
    found_index = -1
    for i, tpl in enumerate(node_heap):
        _, b = tpl
        if b == node:
            found_index = i
            break

    if found_index != -1:
        # BUG FIX: Direct assignment `node_heap[i] = dist_node` does not maintain heap property.
        # To correctly update an element in a heapq, it must be removed and then re-added.
        # This is inefficient (O(N) for pop and heapify) but preserves correctness for heapq.
        node_heap.pop(found_index) # Remove the old entry
        heapify(node_heap)         # Rebuild the heap to maintain its property
    
    heappush(node_heap, dist_node) # Add the new (or updated) entry
    return None

"""
Shortest Path

dijkstra

Implements Dijkstra's algorithm for finding a shortest path between two nodes in a directed graph.

Input:
   length_by_edge: A dict with every directed graph edge's length keyed by its corresponding ordered pair of nodes
   startnode: A node
   goalnode: A node

Precondition:
    all(length > 0 for length in length_by_edge.values())

Output:
    The length of the shortest path from startnode to goalnode in the input graph
"""
