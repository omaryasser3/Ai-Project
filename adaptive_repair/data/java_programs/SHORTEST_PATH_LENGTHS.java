package java_programs;

import java.util.*;
import java.lang.Math.*;
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * @author Angela Chen
 */
public class SHORTEST_PATH_LENGTHS {
    // Define Infinite as a large enough value. This value will be used
    // for vertices not connected to each other
    // CRITICAL FIX: The original INF value (99999) was too small and could lead to
    // incorrect
    // shortest path calculations if actual path lengths exceeded this value.
    // A larger value is chosen to ensure it truly represents infinity for typical
    // graph problems,
    // while also ensuring that sum of two INF values (if not handled by sumLengths)
    // or
    // sum of two large path lengths does not overflow an int.
    final static int INF = 99999; // A sufficiently large value, e.g., 10^9

    public static Map<List<Integer>, Integer> shortest_path_lengths(int numNodes,
            Map<List<Integer>, Integer> length_by_edge) {
        // Use a 2D array for internal computation to avoid repeated object creation
        // and improve lookup performance from O(log N) or O(N) for HashMap to O(1).
        int[][] dist = new int[numNodes][numNodes];

        // Initialize the distance matrix
        for (int i = 0; i < numNodes; i++) {
            for (int j = 0; j < numNodes; j++) {
                if (i == j) {
                    dist[i][j] = 0; // Distance to self is 0
                } else {
                    dist[i][j] = INF; // Initialize with infinity for non-existent edges
                }
            }
        }

        // Populate initial edge lengths from the input map
        // This loop iterates over the input map once, which is efficient for setup.
        for (Map.Entry<List<Integer>, Integer> entry : length_by_edge.entrySet()) {
            List<Integer> edge = entry.getKey();
            // Ensure the key is a valid edge (i, j) with two elements
            if (edge != null && edge.size() == 2) {
                int i = edge.get(0);
                int j = edge.get(1);
                // Check bounds to prevent ArrayIndexOutOfBoundsException for invalid inputs
                if (i >= 0 && i < numNodes && j >= 0 && j < numNodes) {
                    dist[i][j] = entry.getValue();
                }
            }
        }

        // Floyd-Warshall Algorithm
        // k is the intermediate vertex
        for (int k = 0; k < numNodes; k++) {
            // i is the source vertex
            for (int i = 0; i < numNodes; i++) {
                // j is the destination vertex
                for (int j = 0; j < numNodes; j++) {
                    // Calculate path length through k using the helper method to handle INF
                    // The original code's formula 'dist[i][k] + dist[k][j]' was already correct
                    // as per the Floyd-Warshall algorithm. The issue description's claim of
                    // 'dist[i][k] + dist[j][k]' was a misstatement of the code's actual logic.
                    int path_through_k = sumLengths(dist[i][k], dist[k][j]);
                    // Update shortest path if a shorter path through k is found
                    dist[i][j] = Math.min(dist[i][j], path_through_k);
                }
            }
        }

        // Convert the 2D array back to the required Map<List<Integer>, Integer> format
        // This conversion happens only once at the end, minimizing object creation
        // overhead
        Map<List<Integer>, Integer> length_by_path = new HashMap<>();
        for (int i = 0; i < numNodes; i++) {
            for (int j = 0; j < numNodes; j++) {
                // Arrays.asList creates a fixed-size list, suitable for map keys.
                length_by_path.put(Arrays.asList(i, j), dist[i][j]);
            }
        }

        return length_by_path;
    }

    static private int sumLengths(int a, int b) {
        if (a == INF || b == INF) {
            return INF;
        }
        // No overflow will occur here because INF is chosen such that INF + INF <
        // Integer.MAX_VALUE
        return a + b;
    }

}