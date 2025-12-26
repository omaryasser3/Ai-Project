package java_programs;
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * @author derricklin
 */
public class FIND_IN_SORTED {
    public static int binsearch(int[] arr, int x, int start, int end) {
        // Base case: if the search range is empty, the element is not found.
        // The 'end' parameter is exclusive, so start == end means an empty range.
        if (start >= end) {
            return -1;
        }

        int mid = start + (end - start) / 2; // Calculate mid-point, preventing potential overflow

        if (x < arr[mid]) {
            // If x is less than arr[mid], search in the left half (excluding mid)
            return binsearch(arr, x, start, mid);
        } else if (x > arr[mid]) {
            // If x is greater than arr[mid], search in the right half (excluding mid)
            // The original bug was here: including 'mid' in the new range (mid, end)
            // could lead to infinite recursion if mid was the only element left and x > arr[mid].
            // Corrected to start the new range from 'mid + 1'.
            return binsearch(arr, x, mid + 1, end);
        } else {
            // If x is equal to arr[mid], we found the element
            return mid;
        }
    }

    public static int find_in_sorted(int[] arr, int x) {
        // Initial call to binsearch with the full array range [0, arr.length)
        return binsearch(arr, x, 0, arr.length);
    }
}