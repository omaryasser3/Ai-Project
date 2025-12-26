package java_programs;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// CRITICAL: The Node type parameter must extend an interface that defines getSuccessors().
// For example, an interface like this is implicitly required for the generic method to compile:
// public interface GraphNode<N extends GraphNode<N>> {
//     List<N> getSuccessors();
// }
// This interface definition is NOT included in the output as per instructions,
// but it is a necessary assumption for the Java code to be syntactically correct.

public class TOPOLOGICAL_ORDERING {

    public static <Node extends GraphNode<Node>> List<Node> topologicalOrdering(Iterable<Node> directedGraph) {
        // Step 1: Calculate in-degrees for all nodes.
        // The 'inDegree' map stores the count of unprocessed predecessors for each node.
        // Initializing all in-degrees to 0. This takes O(V) time.
        Map<Node, Integer> inDegree = new HashMap<>();
        for (Node node : directedGraph) {
            inDegree.put(node, 0);
        }

        // Populate in-degrees by iterating through all nodes and their successors.
        // Each edge (u -> v) increments inDegree[v]. This takes O(V + E) time.
        for (Node node : directedGraph) {
            for (Node successor : node.getSuccessors()) {
                // Assuming all successors returned by node.getSuccessors() are also
                // nodes present in the 'directedGraph' iterable.
                inDegree.put(successor, inDegree.get(successor) + 1);
            }
        }

        // Step 2: Initialize the queue with all nodes that have an in-degree of 0.
        // These are the nodes with no predecessors, or whose predecessors have all been processed.
        // 'orderedNodes' serves efficiently as both the queue and the final result list.
        // This takes O(V) time.
        List<Node> orderedNodes = new ArrayList<>();
        for (Node node : directedGraph) {
            if (inDegree.get(node) == 0) {
                orderedNodes.add(node); // Enqueue node (O(1) amortized)
            }
        }

        // Step 3: Process nodes from the queue.
        // 'i' acts as the head pointer for our queue (orderedNodes).
        // This allows O(1) dequeue operations without modifying the list structure
        // until the end, making it highly efficient.
        int i = 0;
        while (i < orderedNodes.size()) {
            Node currentNode = orderedNodes.get(i); // Dequeue currentNode (O(1))
            i++; // Advance queue head

            // For each successor of the currentNode:
            // Each edge is processed exactly once across all iterations of the while loop.
            for (Node successor : currentNode.getSuccessors()) {
                // Decrement the in-degree of the successor. This signifies that one of its
                // predecessors (currentNode) has been processed. This is an O(1) operation.
                inDegree.put(successor, inDegree.get(successor) - 1);
                
                // If the successor's in-degree becomes 0, it means all its predecessors
                // have now been processed and added to the order. So, the successor can
                // now be added to the queue. This is an O(1) operation.
                if (inDegree.get(successor) == 0) {
                    orderedNodes.add(successor); // Enqueue successor (O(1) amortized)
                }
            }
        }
        
        // Note: If the graph contains a cycle, len(orderedNodes) will be less
        // than the total number of unique nodes in the graph. For a valid
        // topological sort, the graph must be a Directed Acyclic Graph (DAG).
        
        return orderedNodes;
    }
}