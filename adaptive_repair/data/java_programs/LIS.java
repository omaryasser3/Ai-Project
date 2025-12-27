package java_programs;
import java.util.*;

public class LIS {
    public static int lis(int[] arr) {
        if (arr == null || arr.length == 0) {
            return 0;
        }

        // tails[k] stores the smallest tail of an increasing subsequence of length k.
        // The array is 1-indexed for convenience, so its size is arr.length + 1.
        // We only care about tails[1] to tails[longest].
        // The values in tails[1...longest] are always sorted in increasing order.
        int[] tails = new int[arr.length + 1];
        int longest = 0; // Current length of the longest increasing subsequence found

        for (int val : arr) {
            // Perform a binary search to find the correct position for 'val' in the 'tails' array.
            // We are looking for the smallest 'k' such that tails[k] >= val.
            // This 'k' will be the length of the LIS ending with 'val'.
            // Arrays.binarySearch returns:
            //   - index if 'val' is found (meaning tails[index] == val)
            //   - (-(insertion point) - 1) if 'val' is not found.
            //     The 'insertion point' is the index where 'val' would be inserted
            //     to maintain the sorted order. It's also the smallest index 'k'
            //     such that tails[k] >= val.
            // The search range is from index 1 (inclusive) to 'longest + 1' (exclusive).
            int idx = Arrays.binarySearch(tails, 1, longest + 1, val);

            int newLength;
            if (idx < 0) {
                // 'val' was not found. Calculate the insertion point.
                // The insertion point is the length of the LIS that 'val' can form.
                newLength = -(idx + 1);
            } else {
                // 'val' was found at 'idx'. This means tails[idx] == val.
                // We can replace it with 'val' itself (no effective change to the value,
                // but conceptually we update the tail for this length). The length remains 'idx'.
                newLength = idx;
            }

            // Update the 'tails' array at the calculated position.
            tails[newLength] = val;

            // If we found a new longest increasing subsequence, update 'longest'.
            if (newLength > longest) {
                longest = newLength;
            }
        }
        return longest;
    }
}