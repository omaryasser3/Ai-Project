package java_programs;

import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

public class KHEAPSORT {

    public static List<Integer> kheapsort(int[] arr, int k) {
        // Use PriorityQueue as a min-heap in Java
        PriorityQueue<Integer> heap = new PriorityQueue<>();

        // Initialize the heap with the first 'k' elements from the array.
        // This part of the initial setup is preserved as per the original code's intent.
        // Ensure we don't go out of bounds if arr.length < k
        for (int i = 0; i < k && i < arr.length; i++) {
            heap.offer(arr[i]);
        }

        List<Integer> output = new ArrayList<>();
        // The original bug was iterating over the *entire* input array 'arr' again,
        // which caused elements arr[0] to arr[k-1] to be re-added to the heap.
        // To fix this, we start iterating from index 'k' onwards.
        // This ensures that each element is added to the heap exactly once.
        for (int i = k; i < arr.length; i++) { // Start from index 'k' instead of 0
            // Add the current element to the heap
            heap.offer(arr[i]);
            // Pop the smallest element from the heap and add it to the output.
            // This maintains the heap size and extracts elements in sorted order.
            Integer popped = heap.poll();
            output.add(popped);
        }

        // After iterating through all elements, the heap will contain the
        // remaining 'k' elements (or fewer if len(arr) < k initially).
        // Pop all remaining elements from the heap and append them to the output.
        while (!heap.isEmpty()) {
            output.add(heap.poll());
        }

        return output;
    }
}