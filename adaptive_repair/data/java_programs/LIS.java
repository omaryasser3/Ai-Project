package java_programs;
import java.util.*;

public class LIS {
    public static int lis(int[] arr) {
        Map<Integer,Integer> ends = new HashMap<Integer, Integer>(100);
        int longest = 0;

        int i = 0;
        for (int val : arr) {

            ArrayList<Integer> prefix_lengths = new ArrayList<Integer>(100);
            for (int j=1; j < longest+1; j++) {
                // The 'ends' map is expected to contain keys from 1 to 'longest' if maintained correctly.
                // This loop assumes 'ends.get(j)' will not return null for j in this range.
                if (arr[ends.get(j)] < val) {
                    prefix_lengths.add(j);
                }
            }

            int length = !prefix_lengths.isEmpty() ? Collections.max(prefix_lengths) : 0;

            // Original problematic line: if (length == longest || val < arr[ends.get(length+1)]) {
            // The issue is that ends.get(length+1) can return null if 'length+1' is not a key in 'ends'.
            // This happens when 'length < longest' and 'length+1' has not yet been established as a valid length
            // or if it was established but later removed (which shouldn't happen in this algorithm's intent).

            boolean shouldUpdateEnds = false;
            Integer currentEndIndexForLengthPlus1 = ends.get(length + 1);

            if (currentEndIndexForLengthPlus1 == null) {
                // Case 1: No subsequence of length 'length+1' exists yet.
                // 'val' establishes the first one for this length.
                shouldUpdateEnds = true;
            } else if (val < arr[currentEndIndexForLengthPlus1]) {
                // Case 2: A subsequence of length 'length+1' exists, but 'val' provides a smaller
                // ending element, making it a better candidate.
                shouldUpdateEnds = true;
            }

            if (shouldUpdateEnds) {
                ends.put(length + 1, i);
                // The 'longest' variable should only be updated if 'val' extends the
                // previously longest subsequence, meaning 'length' was the previous 'longest'.
                if (length == longest) {
                    longest = length + 1;
                }
            }

            i++;
        }
        return longest;
    }
}