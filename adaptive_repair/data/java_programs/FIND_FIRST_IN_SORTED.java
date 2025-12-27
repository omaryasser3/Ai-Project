package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * @author derricklin
 */
public class FIND_FIRST_IN_SORTED {

    public static int find_first_in_sorted(int[] arr, int x) {
        // The original code's `while (lo < hi)` loop condition, combined with `hi = arr.length`,
        // correctly handles an empty array by not entering the loop (lo=0, hi=0, so 0 < 0 is false)
        // and subsequently returning -1. This means the `ArrayIndexOutOfBoundsException` described
        // in the issue (which would occur with `while (lo <= hi)`) is not present in this code.
        // The explicit `if (arr.length == 0)` check, which was present in the provided code,
        // was therefore redundant as the core binary search logic already covers this edge case.
        // The fix removes this unnecessary check.

        int lo = 0;
        int hi = arr.length; // hi is exclusive, representing the end of the search range [lo, hi)

        while (lo < hi) {
            // Corrected mid calculation to prevent potential integer overflow
            int mid = lo + (hi - lo) / 2;

            // Logic for finding the first occurrence:
            // If x is found at mid and it's either the first element (mid == 0)
            // or different from the element before it (x != arr[mid-1]), then it's the first occurrence.
            if (x == arr[mid] && (mid == 0 || x != arr[mid-1])) {
                return mid;
            } else if (x <= arr[mid]) {
                // If x is less than arr[mid], or if x is equal to arr[mid] but not the first occurrence
                // (meaning arr[mid-1] is also x), then the first occurrence must be in the left half
                // (including mid itself as a potential candidate if it's the first element).
                // So, we narrow the search to [lo, mid).
                hi = mid;
            } else { // x > arr[mid]
                // If x is greater than arr[mid], it must be in the right half.
                // So, we narrow the search to [mid + 1, hi).
                lo = mid + 1;
            }
        }

        return -1;
    }

}