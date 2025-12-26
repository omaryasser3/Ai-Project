package java_programs;

import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.HashSet;
import java.util.List;
import java.util.ArrayList;
import java.util.Objects;

// Minimal Node class definition based on usage in the provided code.
// It assumes nodes have a comparable value (e.g., String) and a list of successors.
// equals() and hashCode() are crucial for Node objects to be used as keys in Maps and elements in Sets.
class Node {
    private String value; // Assuming node value is a String for comparison and identification
    private List<Node> successors;

    public Node(String value) {
        this.value = value;
        this.successors = new ArrayList<>();
    }

    public String get_value() {
        return value;
    }

    public List<Node> get_successors() {
        return successors;
    }

    // Method to add a successor, useful for graph construction (not directly used
    // in the provided Python code, but good practice)
    public void addSuccessor(Node successor) {
        this.successors.add(successor);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Node node = (Node) o;
        return value.equals(node.value); // Nodes are considered equal if their values are equal
    }

    @Override
    public int hashCode() {
        return value.hashCode();
    }
}

// Helper class to represent an edge (fromNode, toNode) for the length_by_edge
// map key.
// Python's tuple (node, next_node) is best represented by a custom class in
// Java.
// equals() and hashCode() are crucial for Edge objects to be used as keys in
// Maps.
class Edge {
    private Node from;
    private Node to;

    public Edge(Node from, Node to) {
        this.from = from;
        this.to = to;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Edge edge = (Edge) o;
        return from.equals(edge.from) && to.equals(edge.to);
    }

    @Override
    public int hashCode() {
        return Objects.hash(from, to);
    }
}

public class SHORTEST_PATH_LENGTH {

    // Helper method to find the node with the minimum distance from a map of nodes
    // and their distances.
    // This corresponds to the Python function `get_node_with_min_distance`.
    private Node get_node_with_min_distance(Map<Node, Double> nodes_distances) {
        Node minNode = null;
        double minDistance = Double.POSITIVE_INFINITY; // Initialize with positive infinity

        for (Map.Entry<Node, Double> entry : nodes_distances.entrySet()) {
            Node node = entry.getKey();
            double distance = entry.getValue();
            if (distance < minDistance) {
                minDistance = distance;
                minNode = node;
            }
        }
        return minNode;
    }

    // Main method to calculate the shortest path length using Dijkstra's algorithm.
    // This corresponds to the Python function `shortest_path_length`.
    public int shortest_path_length(Map<Edge, Integer> length_by_edge, Node startnode, Node goalnode) {
        // Stores the shortest distance found so far from the startnode to each
        // unvisited node.
        // Python's dict with Node keys and float values.
        Map<Node, Double> unvisited_nodes = new HashMap<>();

        // Stores nodes that have already been visited and whose shortest path from
        // startnode is finalized.
        // Python's set with Node objects.
        Set<Node> visited_nodes = new HashSet<>();

        // Initialize the distance to the startnode as 0.
        unvisited_nodes.put(startnode, 0.0);

        // Continue as long as there are unvisited nodes to process.
        while (!unvisited_nodes.isEmpty()) {
            // Get the unvisited node with the smallest known distance.
            Node node = get_node_with_min_distance(unvisited_nodes);
            double distance = unvisited_nodes.get(node);

            // Remove the current node from the set of unvisited nodes.
            unvisited_nodes.remove(node);

            // If the current node is the goal node, we have found the shortest path.
            // The Python code returns an int, so we cast the double distance.
            // This implies distances are expected to be whole numbers or can be truncated.
            if (node.get_value().equals(goalnode.get_value())) {
                return (int) distance;
            }

            // Mark the current node as visited.
            visited_nodes.add(node);

            // Explore neighbors (successors) of the current node.
            for (Node next_node : node.get_successors()) {
                // If the successor has already been visited, skip it.
                if (visited_nodes.contains(next_node)) {
                    continue;
                }

                // If the successor has not been discovered yet, initialize its distance to
                // infinity.
                if (!unvisited_nodes.containsKey(next_node)) {
                    unvisited_nodes.put(next_node, Double.POSITIVE_INFINITY);
                }

                double current_next_node_distance = unvisited_nodes.get(next_node);

                // Get the length of the edge between the current node and the successor.
                // The Python comment "We assume valid graph where all successors have defined
                // edge lengths."
                // implies that `length_by_edge.get()` will not return null for valid
                // successors.
                Integer edge_length_obj = length_by_edge.get(new Edge(node, next_node));
                int edge_length = (edge_length_obj != null) ? edge_length_obj : 0; // Fallback, though should not be
                                                                                   // null per assumption.

                // Calculate the distance to the successor through the current node.
                double new_path_candidate = distance + edge_length;

                // Update the shortest distance to the successor if a shorter path is found.
                unvisited_nodes.put(next_node, Math.min(current_next_node_distance, new_path_candidate));
            }
        }

        // If the loop finishes and the goal node was not reached, it means the goal is
        // unreachable.
        // Return positive infinity, cast to int.
        return (int) Double.POSITIVE_INFINITY;
    }
}