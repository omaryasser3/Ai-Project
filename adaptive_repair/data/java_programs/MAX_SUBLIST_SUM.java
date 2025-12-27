package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class MAX_SUBLIST_SUM {
    public static int max_sublist_sum(int[] arr) {
        // Handle empty or null array case. Consistent with original behavior where
        // an empty array would result in max_so_far remaining 0.
        if (arr == null || arr.length == 0) {
            return 0;
        }

        int max_so_far = Integer.MIN_VALUE; // Initialize to smallest possible value to correctly track negative sums
        int max_ending_here = 0; // Current sum ending at the current position
        boolean all_negatives = true; // Flag to detect if all elements are negative
        int max_single_element = Integer.MIN_VALUE; // To store the largest (least negative) single element

        for (int x : arr) {
            // Track if any non-negative number is encountered
            if (x >= 0) {
                all_negatives = false;
            }
            // Keep track of the largest single element, needed if all numbers are negative
            max_single_element = Math.max(max_single_element, x);

            max_ending_here = max_ending_here + x;
            // If max_ending_here becomes negative, it means this sublist is contributing negatively.
            // Reset it to 0 to start a new potential sublist from the next element.
            // This is a core part of Kadane's algorithm for positive sums.
            if (max_ending_here < 0) {
                max_ending_here = 0;
            }
            // Update the overall maximum sum found so far
            max_so_far = Math.max(max_so_far, max_ending_here);
        }

        // Special handling for arrays where all elements are negative.
        // In such cases, max_so_far would be 0 (due to max_ending_here resets).
        // The correct answer for an all-negative array is the largest (least negative) single element.
        if (all_negatives) {
            return max_single_element;
        } else {
            return max_so_far;
        }
    }
}