class DSU:
    """
    A Disjoint Set Union (DSU) data structure with path compression and union by rank.
    """
    def __init__(self):
        # parent[i] stores the parent of element i. If parent[i] == i, i is the representative.
        self.parent = {}
        # rank[i] stores the rank of the tree rooted at i. Used for union by rank heuristic.
        self.rank = {}

    def make_set(self, i):
        """
        Initializes a new set containing only element i.
        If i already exists, this operation does nothing.
        """
        if i not in self.parent:
            self.parent[i] = i
            self.rank[i] = 0

    def find(self, i):
        """
        Finds the representative (root) of the set containing element i.
        Applies path compression to flatten the tree structure.
        """
        if self.parent[i] == i:
            return i
        # Path compression: set parent[i] directly to the root
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        """
        Merges the sets containing elements i and j.
        Returns True if a merge occurred, False if i and j were already in the same set.
        Applies union by rank heuristic to keep trees balanced.
        """
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            # Union by rank: attach the smaller rank tree under the root of the larger rank tree.
            # If ranks are equal, pick one as root and increment its rank.
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False

def minimum_spanning_tree(weight_by_edge):
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
    dsu = DSU()
    mst_edges = set()

    # Kruskal's algorithm: Sort all edges by weight in non-decreasing order.
    for edge in sorted(weight_by_edge, key=weight_by_edge.__getitem__):
        u, v = edge
        
        # Ensure both nodes are initialized in the DSU structure.
        # This creates a new set for each node if it hasn't been seen before.
        dsu.make_set(u)
        dsu.make_set(v)

        # Find the representatives (roots) of the sets containing u and v.
        # This implicitly performs path compression.
        root_u = dsu.find(u)
        root_v = dsu.find(v)

        # If u and v are in different components (their representatives are different),
        # adding this edge will not form a cycle.
        if root_u != root_v:
            mst_edges.add(edge)
            # Merge the two components. This implicitly performs union by rank.
            dsu.union(u, v)

    return mst_edges