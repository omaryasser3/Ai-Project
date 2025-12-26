package java_programs;

public class SHORTEST_PATHS {

    // Define Infinite as a large enough value. This value will be used
    // for vertices not connected to each other
    public static final int INF = 99999;

    // Helper classes for the shortest_paths methods.
    // For the purpose of this single-file translation, they are nested static classes.

    public static class Node {
        private int value; // Assuming node values are integers for graph algorithms

        public Node(int value) {
            this.value = value;
        }

        public int getValue() {
            return this.value;
        }

        @Override
        public String toString() {
            return String.valueOf(this.value);
        }

        // Overriding equals and hashCode is good practice if Node objects
        // were to be used as keys in collections. Here, their integer values are used as keys.
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Node node = (Node) o;
            return value == node.value;
        }

        @Override
        public int hashCode() {
            return Integer.hashCode(value);
        }
    }

    public static class WeightedEdge {
        public Node node1;
        public Node node2;
        public int weight;

        public WeightedEdge(Node node1, Node node2, int weight) {
            this.node1 = node1;
            this.node2 = node2;
            this.weight = weight;
        }
    }

    // Helper Pair class for the first shortest_paths method's map keys.
    // This is equivalent to Python's tuple (u, v) used as a dictionary key.
    private static class Pair<K, V> {
        private K first;
        private V second;

        public Pair(K first, V second) {
            this.first = first;
            this.second = second;
        }

        public K getFirst() {
            return first;
        }

        public V getSecond() {
            return second;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Pair<?, ?> pair = (Pair<?, ?>) o;
            return first.equals(pair.first) && second.equals(pair.second);
        }

        @Override
        public int hashCode() {
            // A simple hash code combining the hash codes of the two elements
            return 31 * first.hashCode() + second.hashCode();
        }
    }

    // First shortest_paths method (corresponding to the first Python definition)
    // @param sourceValue The integer value of the source node.
    // @param weightByEdge A map where keys are Pair<Integer, Integer> representing (u, v) node values,
    //                     and values are the edge weights.
    // @return A map from node integer values to their shortest path weights from the source.
    public static java.util.Map<Integer, Integer> shortest_paths(int sourceValue, java.util.Map<Pair<Integer, Integer>, Integer> weightByEdge) {
        java.util.Map<Integer, Integer> weightByNode = new java.util.HashMap<>();
        java.util.Set<Integer> allNodes = new java.util.HashSet<>();

        // Collect all unique node values from the edges
        for (Pair<Integer, Integer> edge : weightByEdge.keySet()) {
            allNodes.add(edge.getFirst());
            allNodes.add(edge.getSecond());
        }

        // Initialize distances to all nodes as infinite, except for the source
        for (Integer nodeVal : allNodes) {
            weightByNode.put(nodeVal, SHORTEST_PATHS.INF);
        }

        weightByNode.put(sourceValue, 0);
        
        // Bellman-Ford algorithm: Relax all edges |V| times
        // (or |V|-1 times for shortest paths, an extra iteration for negative cycle detection)
        for (int i = 0; i < allNodes.size(); i++) { 
            for (java.util.Map.Entry<Pair<Integer, Integer>, Integer> entry : weightByEdge.entrySet()) {
                Pair<Integer, Integer> edge = entry.getKey();
                Integer edgeWeight = entry.getValue();
                
                Integer u = edge.getFirst();
                Integer v = edge.getSecond();
                
                // Calculate potential new distance to v through u
                int newDistToVThroughU = SHORTEST_PATHS.INF;
                // Ensure u is reachable (its current distance is not INF)
                if (weightByNode.getOrDefault(u, SHORTEST_PATHS.INF) != SHORTEST_PATHS.INF) { 
                    newDistToVThroughU = weightByNode.getOrDefault(u, SHORTEST_PATHS.INF) + edgeWeight;
                }
                
                // Update distance to v if a shorter path is found
                weightByNode.put(v, Math.min(newDistToVThroughU, weightByNode.getOrDefault(v, SHORTEST_PATHS.INF)));
            }
        }
        return weightByNode;
    }

    // Second shortest_paths method (corresponding to the second Python definition, intended as overload)
    // @param source The source Node object.
    // @param weightByEdge A list of WeightedEdge objects.
    // @return A map from node integer values to their shortest path weights from the source.
    public static java.util.Map<Integer, Integer> shortest_paths(Node source, java.util.List<WeightedEdge> weightByEdge) {
        java.util.Map<Integer, Integer> weightByNode = new java.util.HashMap<>();
        java.util.Set<Integer> allNodes = new java.util.HashSet<>();

        // Collect all unique node values from the edges
        for (WeightedEdge edge : weightByEdge) {
            allNodes.add(edge.node1.getValue());
            allNodes.add(edge.node2.getValue());
        }

        // Initialize distances to all nodes as infinite, except for the source
        for (Integer nodeVal : allNodes) {
            weightByNode.put(nodeVal, SHORTEST_PATHS.INF);
        }

        weightByNode.put(source.getValue(), 0);
        
        // Bellman-Ford algorithm: Relax all edges |V| times
        for (int i = 0; i < allNodes.size(); i++) { 
            for (WeightedEdge edge : weightByEdge) {
                Integer uVal = edge.node1.getValue();
                Integer vVal = edge.node2.getValue();
                int currentEdgeWeight = edge.weight; // Use the original edge weight for relaxation

                // Calculate potential new distance to vVal through uVal
                int newDistToVThroughU = SHORTEST_PATHS.INF;
                // Ensure uVal is reachable (its current distance is not INF)
                if (weightByNode.getOrDefault(uVal, SHORTEST_PATHS.INF) != SHORTEST_PATHS.INF) { 
                    newDistToVThroughU = weightByNode.getOrDefault(uVal, SHORTEST_PATHS.INF) + currentEdgeWeight;
                }
                
                // Update distance to vVal if a shorter path is found
                weightByNode.put(vVal, Math.min(newDistToVThroughU, weightByNode.getOrDefault(vVal, SHORTEST_PATHS.INF)));
            }
        }
        return weightByNode;
    }
}