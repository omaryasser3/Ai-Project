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
        if (arr == null || arr.length == 0) {
            return 0; // Consistent with original behavior for empty/null arrays, though problem implies non-empty.
        }

        int max_so_far = arr[0]; // Initialize with the first element to handle all-negative arrays correctly
        int max_ending_here = arr[0]; // Initialize with the first element

        // Iterate from the second element
        for (int i = 1; i < arr.length; i++) {
            int x = arr[i];
            // Kadane's algorithm: The maximum sum ending at the current position 'x'
            // is either 'x' itself (starting a new sublist) or 'x' added to the
            // maximum sum ending at the previous position (extending the current sublist).
            // This correctly discards negative prefixes.
            max_ending_here = Math.max(x, max_ending_here + x);
            
            // Update the overall maximum sum found so far
            max_so_far = Math.max(max_so_far, max_ending_here);
        }

        return max_so_far;
    }
}