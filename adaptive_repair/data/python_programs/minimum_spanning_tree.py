def minimum_spanning_tree(weight_by_edge):
    # DSU (Disjoint Set Union) data structure implementation
    parent = {}
    rank = {}

    def find(i):
        # If node i is encountered for the first time, initialize its DSU entry
        if i not in parent:
            parent[i] = i
            rank[i] = 0
            return i

        # Path compression: Make every node on the path point directly to the root
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)

        if root_i != root_j:
            # Union by rank: Attach the smaller rank tree under the root of the larger rank tree
            if rank[root_i] < rank[root_j]:
                parent[root_i] = root_j
            elif rank[root_i] > rank[root_j]:
                parent[root_j] = root_i
            else:
                parent[root_j] = root_i
                rank[root_i] += 1 # Increment rank if ranks were equal
            return True  # A union operation occurred
        return False # i and j were already in the same set

    mst_edges = set()

    # Kruskal's algorithm: Iterate through edges sorted by weight
    for edge in sorted(weight_by_edge, key=weight_by_edge.__getitem__):
        u, v = edge
        # If u and v are in different components, add the edge to MST and union their components
        if union(u, v):
            mst_edges.add(edge)

    return mst_edges




"""
Minimum Spanning Tree


Kruskal's algorithm implementation.

Input:
    weight_by_edge: A dict of the form {(u, v): weight} for every undirected graph edge {u, v}

Precondition:
    The input graph is connected

Output:
    A set of edges that connects all the vertices of the input graph and has the least possible total weight.

Example:
    >>> minimum_spanning_tree({
    ...     (1, 2): 10,
    ...     (2, 3): 15,
    ...     (3, 4): 10,
    ...     (1, 4): 10
    ... })
    {(1, 2), (3, 4), (1, 4)}
"""
