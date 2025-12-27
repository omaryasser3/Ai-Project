package java_programs;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class KTH {

    public static int kth(List<Integer> arr, int k) {
        // Handle empty array or invalid k (optional, but good practice for robustness)
        if (arr == null || arr.isEmpty()) {
            throw new IllegalArgumentException("Array cannot be empty");
        }
        if (k < 0 || k >= arr.size()) {
            throw new IndexOutOfBoundsException(
                String.format("k (%d) is out of bounds for array of length %d", k, arr.size())
            );
        }

        // Optimize: Choose a random pivot to improve average-case time complexity
        // and mitigate worst-case O(N^2) scenarios (e.g., sorted/reverse-sorted arrays).
        Random rand = new Random();
        int pivotIdx = rand.nextInt(arr.size());
        int pivot = arr.get(pivotIdx);

        List<Integer> below = new ArrayList<>();
        List<Integer> above = new ArrayList<>();
        // Elements equal to the pivot are implicitly handled by not being in 'below' or 'above'
        // and are covered by the 'else' branch.
        for (int x : arr) {
            if (x < pivot) {
                below.add(x);
            } else if (x > pivot) {
                above.add(x);
            }
        }

        int numLess = below.size();
        // num_lessoreq represents the count of elements that are less than or equal to the pivot.
        // This includes elements in 'below' and elements equal to the pivot.
        // It can be calculated as len(arr) - len(above).
        int numLessOrEq = arr.size() - above.size();
        
        if (k < numLess) {
            // The k-th element is in the 'below' partition.
            // Its 0-indexed position relative to 'below' remains 'k'.
            return kth(below, k);
        } else if (k >= numLessOrEq) {
            // The k-th element is in the 'above' partition.
            // Its 0-indexed position relative to 'above' needs to be adjusted.
            // We subtract all elements that are less than or equal to the pivot.
            return kth(above, k - numLessOrEq);
        } else {
            // The k-th element is one of the elements equal to the pivot.
            // This occurs when num_less <= k < num_lessoreq.
            return pivot;
        }
    }
}