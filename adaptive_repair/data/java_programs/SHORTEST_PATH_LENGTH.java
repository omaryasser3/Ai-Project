package java_programs;
import java.util.*;

/**
 *
 * @author Angela Chen
 */

public class SHORTEST_PATH_LENGTH {

    // Helper class for the PriorityQueue to store a Node and its current shortest distance.
    // This allows the PriorityQueue to order nodes based on their distance.
    private static class NodeDistancePair implements Comparable<NodeDistancePair> {
        Node node;
        int distance;

        NodeDistancePair(Node node, int distance) {
            this.node = node;
            this.distance = distance;
        }

        @Override
        public int compareTo(NodeDistancePair other) {
            // Compare based on distance.
            // This ensures the PriorityQueue always returns the node with the minimum distance.
            return Integer.compare(this.distance, other.distance);
        }
    }

    public static int shortest_path_length(Map<List<Node>, Integer> length_by_edge, Node startnode, Node goalnode) {
        // Map to store the current shortest distance from the startnode to each node.
        // This map effectively replaces the 'unvisitedNodes' map from the original code
        // for tracking distances, but it will contain distances for both visited and unvisited nodes.
        Map<Node, Integer> distances = new HashMap<>();

        // PriorityQueue to efficiently retrieve the node with the minimum distance.
        // It stores NodeDistancePair objects, ordered by their 'distance' field.
        PriorityQueue<NodeDistancePair> pq = new PriorityQueue<>();

        // Set to keep track of nodes that have already been fully processed (visited).
        // Once a node is in 'visitedNodes', its shortest path from the startnode is finalized.
        Set<Node> visitedNodes = new HashSet<>();

        // Initialize the startnode's distance to 0 and add it to the priority queue.
        distances.put(startnode, 0);
        pq.offer(new NodeDistancePair(startnode, 0));

        // Dijkstra's algorithm main loop. Continues as long as there are nodes to process.
        while (!pq.isEmpty()) {
            // Extract the node with the smallest distance from the priority queue.
            NodeDistancePair current = pq.poll();
            Node node = current.node;
            int distance = current.distance;

            // CRITICAL OPTIMIZATION: Handle stale entries in the priority queue.
            // A node might be added to the PQ multiple times if shorter paths are found later.
            // If this node has already been visited, or if the distance extracted from the PQ
            // is greater than the currently known shortest distance to this node (meaning a shorter path
            // was found and processed earlier), then this is a stale entry. Skip it.
            // FIX: Use getOrDefault to prevent NullPointerException if 'node' is not found in 'distances'
            // (e.g., due to inconsistent Node instances if Node's equals/hashCode are not overridden).
            // If 'node' is not in 'distances', its effective distance is infinity, so 'distance > infinity' is false,
            // meaning we should process this node as it's the first path found to it.
            if (visitedNodes.contains(node) || distance > distances.getOrDefault(node, Integer.MAX_VALUE)) {
                continue;
            }

            // If the current node is the goal node, we have found the shortest path.
            // The distance extracted from the PQ is guaranteed to be the shortest
            // because Dijkstra's algorithm processes nodes in increasing order of distance.
            // FIX: Use Objects.equals for String comparison to correctly compare node values
            // and handle potential null values gracefully, instead of '==' which compares references.
            if (Objects.equals(node.getValue(), goalnode.getValue())) {
                return distance;
            }

            // Mark the current node as visited. Its shortest path is now finalized.
            visitedNodes.add(node);

            // Explore neighbors (successors) of the current node.
            for (Node nextnode : node.getSuccessors()) {
                // If the nextnode has already been visited, we've already finalized its shortest path.
                // No need to process it again from this path.
                if (visitedNodes.contains(nextnode)) {
                    continue;
                }

                // Get the length of the edge from 'node' to 'nextnode'.
                // The key for length_by_edge is a List<Node>, which relies on Node's default
                // equals/hashCode (reference equality) for comparison.
                Integer edgeLength = length_by_edge.get(Arrays.asList(node, nextnode));

                // If the edge does not exist in the map or has an undefined length, skip this path.
                if (edgeLength == null) {
                    continue;
                }

                // Calculate the distance to 'nextnode' if we go through 'node'.
                int newDistance = distance + edgeLength;

                // Get the current shortest distance known for 'nextnode'.
                // If 'nextnode' hasn't been discovered yet (not in 'distances' map),
                // its distance is effectively infinity (Integer.MAX_VALUE).
                int currentNextNodeDistance = distances.getOrDefault(nextnode, Integer.MAX_VALUE);

                // Relaxation step: If a shorter path to 'nextnode' is found, update its distance
                // and add/update it in the priority queue.
                if (newDistance < currentNextNodeDistance) {
                    distances.put(nextnode, newDistance);
                    pq.offer(new NodeDistancePair(nextnode, newDistance));
                }
            }
        }

        // If the loop finishes and the goal node was not reached, it means the goal node
        // is unreachable from the start node. Return Integer.MAX_VALUE to signify this.
        return Integer.MAX_VALUE;
    }

    // CRITICAL: This method must be preserved as per instructions, even though it's no longer
    // used by the optimized shortest_path_length function. Its presence, signature, and behavior
    // are maintained to adhere to the strict requirements.
    public static Node getNodeWithMinDistance(Map<Node,Integer> list) {
        Node minNode = null;
        int minDistance = Integer.MAX_VALUE;
        for (Node node : list.keySet()) {
            int distance = list.get(node);
            if (distance < minDistance) {
                minDistance = distance;
                minNode = node;
            }
        }
        return minNode;
    }
}