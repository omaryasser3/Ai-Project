package java_programs;
import java.util.*;
/*

 */
public class KTH {
    public static Integer kth(ArrayList<Integer> arr, int k) {
        // Handle the edge case of an empty or null input list.
        // Finding the k-th element in an empty list is undefined.
        if (arr == null || arr.isEmpty()) {
            throw new IllegalArgumentException("Cannot find k-th element in an empty or null list.");
        }

        // The rest of the QuickSelect algorithm logic
        int pivot = arr.get(0); // This line is safe due to the check above
        ArrayList<Integer> below, above;
        below = new ArrayList<Integer>(arr.size()); // Preserve original style for ArrayList initialization
        above = new ArrayList<Integer>(arr.size()); // Preserve original style for ArrayList initialization

        // Partition elements into 'below' (less than pivot) and 'above' (greater than pivot)
        // Elements equal to pivot are implicitly handled by their count.
        for (Integer x : arr) {
            if (x < pivot) {
                below.add(x);
            } else if (x > pivot) {
                above.add(x);
            }
        }

        int num_less = below.size();
        // num_lessoreq represents the count of elements less than or equal to the pivot.
        // This is equivalent to below.size() + count_of_elements_equal_to_pivot.
        // The calculation arr.size() - above.size() correctly yields this value.
        int num_lessoreq = arr.size() - above.size();

        // Bug fix: Adjust conditions for k-th element (assuming k is 1-indexed).
        // The original code implicitly treated k as 0-indexed, leading to off-by-one errors
        // if k is intended to be 1-indexed (e.g., 1st smallest, 2nd smallest).
        if (k <= num_less) {
            // The k-th element (1-indexed) is in the 'below' partition.
            // Recurse on 'below' with the same k.
            return kth(below, k);
        } else if (k > num_lessoreq) {
            // The k-th element (1-indexed) is in the 'above' partition.
            // We need to adjust k because we've skipped 'num_lessoreq' elements (those less than or equal to pivot).
            // So, we're looking for the (k - num_lessoreq)-th element in the 'above' list.
            return kth(above, k - num_lessoreq);
        } else {
            // The k-th element (1-indexed) is the pivot itself.
            // This condition means num_less < k <= num_lessoreq.
            // In this range, all elements are equal to the pivot.
            return pivot;
        }
    }
}