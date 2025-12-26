package java_programs;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

// Define an Edge class as it's used in the MINIMUM_SPANNING_TREE method.
// It needs to be comparable for sorting by weight.
class Edge implements Comparable<Edge> {
    Object node1;
    Object node2;
    int weight; // Assuming integer weights

    public Edge(Object node1, Object node2, int weight) {
        this.node1 = node1;
        this.node2 = node2;
        this.weight = weight;
    }

    // For sorting edges by weight in ascending order
    @Override
    public int compareTo(Edge other) {
        return Integer.compare(this.weight, other.weight);
    }

    // Optional: Override equals and hashCode if Edge objects need to be compared by content
    // rather than just instance identity when stored in a Set.
    // For this problem, the Python code adds the *instance* of the edge, so default Object equals/hashCode is often sufficient.
    // If uniqueness in the set should be based on (node1, node2, weight) regardless of instance,
    // these methods would need to be implemented.
}

// DSU (Disjoint Set Union) data structure
// This class is not public, so it can reside in the same file as MINIMUM_SPANNING_TREE.java
class DSU {
    private Map<Object, Object> parent;
    private Map<Object, Integer> rank;

    public DSU() {
        this.parent = new HashMap<>();
        this.rank = new HashMap<>();
    }

    public Object find(Object node) {
        // If node is not yet in the DSU, initialize it as a new set.
        // Each node initially is its own parent (representative of its own set) and has rank 0.
        if (!parent.containsKey(node)) {
            parent.put(node, node);
            rank.put(node, 0);
            return node;
        }

        // Path compression: set node's parent directly to the representative
        if (parent.get(node) == node) {
            return node;
        }
        // Recursively find the root and set it as the direct parent
        Object root = find(parent.get(node));
        parent.put(node, root);
        return root;
    }

    public boolean union(Object node1, Object node2) {
        Object root1 = find(node1);
        Object root2 = find(node2);

        if (!root1.equals(root2)) { // Use .equals() for object content comparison
            // Union by rank: Attach the smaller rank tree under the root of the larger rank tree.
            // If ranks are equal, pick one as root and increment its rank.
            int rank1 = rank.get(root1);
            int rank2 = rank.get(root2);

            if (rank1 < rank2) {
                parent.put(root1, root2);
            } else if (rank2 < rank1) {
                parent.put(root2, root1);
            } else { // Ranks are equal
                parent.put(root1, root2);
                rank.put(root2, rank2 + 1); // Increment rank of the new root
            }
            return true; // Indicates a successful union (components were distinct)
        }
        return false; // Indicates nodes were already in the same component
    }
}

public class MINIMUM_SPANNING_TREE {
    public static Set<Edge> minimum_spanning_tree(List<Edge> weightedEdges) {
        DSU dsu = new DSU(); // Create an instance of the DSU data structure
        Set<Edge> minSpanningTree = new HashSet<>();

        // Sort edges by weight (ascending)
        // The Edge class must implement Comparable<Edge> for this to work.
        Collections.sort(weightedEdges);

        for (Edge edge : weightedEdges) {
            Object vertex_u = edge.node1;
            Object vertex_v = edge.node2;

            // The DSU's find/union methods now handle node initialization internally.
            // We just attempt to union the sets containing vertex_u and vertex_v.
            if (dsu.union(vertex_u, vertex_v)) {
                minSpanningTree.add(edge); // Add edge to MST if it connects two different components
            }
        }
        
        return minSpanningTree;
    }
}