package java_programs;

import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

// The Edge class is assumed to exist and implement Comparable<Edge>
// and provide methods like getNode1(), getNode2(), and getWeight().
// Example structure for Edge (not part of the output, but for context):
// class Edge implements Comparable<Edge> {
//     private Object node1;
//     private Object node2;
//     private int weight;
//
//     public Edge(Object node1, Object node2, int weight) { /* ... */ }
//     public Object getNode1() { return node1; }
//     public Object getNode2() { return node2; }
//     public int getWeight() { return weight; }
//
//     @Override
//     public int compareTo(Edge other) { return Integer.compare(this.weight, other.weight); }
//     // For Set operations, if conceptual equality (e.g., (A,B,w) == (B,A,w)) is desired,
//     // equals and hashCode must be overridden. Otherwise, default object identity is used.
// }

public class MINIMUM_SPANNING_TREE {
    /**
     * Minimum spanning tree
     */

    // DSU structure will be managed by these static class attributes
    // _parent maps a node to its parent node in the DSU tree.
    // _size maps a root node to the size of the component it represents (for union by size optimization).
    private static Map<Object, Object> _parent = new HashMap<>();
    private static Map<Object, Integer> _size = new HashMap<>();

    private static void _makeSet(Object node) {
        /** Initializes a new set for a given node if it doesn't exist. */
        if (!MINIMUM_SPANNING_TREE._parent.containsKey(node)) {
            MINIMUM_SPANNING_TREE._parent.put(node, node); // Each node is initially its own parent
            MINIMUM_SPANNING_TREE._size.put(node, 1);      // Each component initially has size 1
        }
    }

    private static Object _find(Object node) {
        /** Finds the representative (root) of the set containing the given node, with path compression. */
        // If the node is its own parent, it's the root of its set
        if (MINIMUM_SPANNING_TREE._parent.get(node) == node) { // Using == for object identity, matching Python's 'is'
            return node;
        }
        // Otherwise, recursively find the root and apply path compression
        MINIMUM_SPANNING_TREE._parent.put(node, MINIMUM_SPANNING_TREE._find(MINIMUM_SPANNING_TREE._parent.get(node)));
        return MINIMUM_SPANNING_TREE._parent.get(node);
    }

    private static boolean _union(Object nodeU, Object nodeV) {
        /** Unites the sets containing node_u and node_v, using union by size optimization. */
        Object rootU = MINIMUM_SPANNING_TREE._find(nodeU);
        Object rootV = MINIMUM_SPANNING_TREE._find(nodeV);

        // If roots are different, they are in different components, so merge them
        if (rootU != rootV) { // Using != for object identity, matching Python's 'is not'
            // Attach smaller tree under root of larger tree (union by size)
            if (MINIMUM_SPANNING_TREE._size.get(rootU) < MINIMUM_SPANNING_TREE._size.get(rootV)) {
                // Swap to ensure rootU is the larger tree's root
                Object temp = rootU;
                rootU = rootV;
                rootV = temp;
            }
            
            MINIMUM_SPANNING_TREE._parent.put(rootV, rootU);
            MINIMUM_SPANNING_TREE._size.put(rootU, MINIMUM_SPANNING_TREE._size.get(rootU) + MINIMUM_SPANNING_TREE._size.get(rootV));
            return true; // Components were successfully merged
        }
        return false; // Nodes were already in the same component
    }

    public static Set<Edge> minimumSpanningTree(List<Edge> weightedEdges) {
        Set<Edge> minSpanningTree = new HashSet<>();

        // Clear DSU state for each new MST calculation
        // This ensures that multiple calls to minimumSpanningTree operate independently.
        MINIMUM_SPANNING_TREE._parent = new HashMap<>();
        MINIMUM_SPANNING_TREE._size = new HashMap<>();

        // Sort edges by weight. This is the dominant step for Kruskal's algorithm, O(E log E).
        // Requires Edge class to implement Comparable<Edge>.
        Collections.sort(weightedEdges);

        for (Edge edge : weightedEdges) {
            Object vertexU = edge.getNode1();
            Object vertexV = edge.getNode2();
            
            // Ensure both vertices are initialized in the DSU structure
            MINIMUM_SPANNING_TREE._makeSet(vertexU);
            MINIMUM_SPANNING_TREE._makeSet(vertexV);

            // Find the representatives (roots) of the components for vertexU and vertexV.
            // This is the 'find' operation in DSU.
            Object rootU = MINIMUM_SPANNING_TREE._find(vertexU);
            Object rootV = MINIMUM_SPANNING_TREE._find(vertexV);

            // The condition `rootU != rootV` correctly checks if
            // vertexU and vertexV belong to different connected components
            // by comparing their root representatives (object identity).
            if (rootU != rootV) {
                minSpanningTree.add(edge);
                // Call the DSU union method to merge the components.
                // This operation, along with find, has an amortized time complexity
                // of nearly O(1) due to path compression and union by size.
                MINIMUM_SPANNING_TREE._union(vertexU, vertexV);
            }
        }
        return minSpanningTree;
    }
}