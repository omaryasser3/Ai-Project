package java_programs;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

// The 'Node' class is assumed to be defined elsewhere and accessible.
// It must have a public method 'getSuccessors()' that returns a List<Node>.
// For Node objects to be used as keys in a HashMap, their equals() and hashCode()
// methods should be properly implemented if object identity is not sufficient for equality.
// For example:
// class Node {
//     // private String id; // Example field
//     // private List<Node> successors; // Example field
//
//     // public Node(String id) { this.id = id; this.successors = new ArrayList<>(); }
//     public List<Node> getSuccessors() {
//         // return this.successors; // Actual implementation
//         return new ArrayList<>(); // Placeholder
//     }
//
//     // @Override
//     // public boolean equals(Object o) { ... }
//     // @Override
//     // public int hashCode() { ... }
// }

public class TOPOLOGICAL_ORDERING {
    public static List<Node> topological_ordering(List<Node> directed_graph) {
        List<Node> orderedNodes = new ArrayList<>();

        // 1. Compute in-degrees for all nodes
        // Initialize all nodes with an in-degree of 0
        Map<Node, Integer> inDegree = new HashMap<>();
        for (Node node : directed_graph) {
            inDegree.put(node, 0);
        }

        // Populate in-degrees by iterating through successors
        for (Node node : directed_graph) {
            for (Node successor : node.getSuccessors()) {
                // Ensure the successor is part of the graph being processed
                // (i.e., it's in the `directed_graph` list). If not, it's an ill-formed graph input.
                if (inDegree.containsKey(successor)) {
                    inDegree.put(successor, inDegree.get(successor) + 1);
                }
            }
        }

        // 2. Initialize the queue (which is `ordered_nodes` in this structure)
        // with nodes that have an in-degree of 0 (no predecessors)
        for (Node node : directed_graph) {
            if (inDegree.get(node) == 0) {
                orderedNodes.add(node);
            }
        }

        int i = 0;
        int listSize = orderedNodes.size(); // Current size of the queue/result list
        
        // 3. Process nodes in the order they are added to ordered_nodes (Kahn's algorithm)
        while (i < listSize) {
            Node node = orderedNodes.get(i); // Get the next node to process (dequeue)
            
            // For each successor of the current node
            for (Node nextNode : node.getSuccessors()) {
                // Decrement the in-degree of the successor
                inDegree.put(nextNode, inDegree.get(nextNode) - 1);
                
                // If the successor's in-degree becomes 0, it means all its predecessors
                // have been processed. Add it to the queue/result list.
                if (inDegree.get(nextNode) == 0) {
                    orderedNodes.add(nextNode);
                    listSize++; // Increment list_size as a new node is added to the queue
                }
            }
            i++;
        }
        
        return orderedNodes;
    }
}