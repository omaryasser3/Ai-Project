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
public class FIND_FIRST_IN_SORTED {

    public static int find_first_in_sorted(int[] arr, int x) {
        int lo = 0;
        int hi = arr.length; // hi is an exclusive upper bound, search space is [lo, hi)

        // The original loop condition `while (lo <= hi)` combined with `hi = arr.length`
        // could lead to `mid` being `arr.length`, causing an ArrayIndexOutOfBoundsException.
        // Changing to `while (lo < hi)` ensures `mid` always points to a valid index.
        while (lo < hi) {
            int mid = (lo + hi) / 2; // Standard floor division

            // This logic implements a standard 'lower bound' binary search.
            // It finds the first position where 'x' could be inserted while maintaining sorted order.
            // If arr[mid] is less than x, then x must be in the right half (after mid).
            if (arr[mid] < x) {
                lo = mid + 1;
            } else { // arr[mid] >= x
                // If arr[mid] is greater than or equal to x, then x could be at mid
                // or in the left half (before mid). So, we narrow the search to [lo, mid].
                hi = mid;
            }
        }

        // After the loop, 'lo' (which is equal to 'hi') will be the index of the first element
        // that is greater than or equal to 'x'.
        // We need to verify if this element is actually 'x' and if 'lo' is a valid index.
        if (lo < arr.length && arr[lo] == x) {
            return lo;
        } else {
            return -1; // Element not found or array is empty
        }
    }

}