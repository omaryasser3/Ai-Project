package java_programs;

import java.util.Arrays;

public class NEXT_PALINDROME {

    // Helper function to compare two int arrays lexicographically
    // Returns 1 if arr1 > arr2, -1 if arr1 < arr2, 0 if arr1 == arr2
    private static int compareArrays(int[] arr1, int[] arr2) {
        int n = arr1.length; // Assuming both arrays have the same length in this context
        for (int i = 0; i < n; i++) {
            if (arr1[i] < arr2[i]) {
                return -1; // arr1 is smaller
            } else if (arr1[i] > arr2[i]) {
                return 1; // arr1 is greater
            }
        }
        return 0; // Arrays are equal
    }

    public static String next_palindrome(int[] digit_list) {
        int n = digit_list.length;

        // Make a copy of the input list to preserve the original for comparison
        // and to allow in-place modification for the increment step.
        int[] current_digits = Arrays.copyOf(digit_list, n);

        // Determine the middle index for the left half.
        // This index will be used for mirroring and for starting carry propagation.
        int mid_idx = (n - 1) / 2;

        // --- Step 1: Construct a candidate palindrome by mirroring the left half of the original number ---
        // Create a temporary list to hold this first mirrored candidate.
        // The left half of this candidate is identical to the original number's left half.
        int[] candidate_palindrome = Arrays.copyOf(current_digits, n);

        // Mirror the left half (including the middle digit for odd n) to the right half.
        for (int k = 0; k < n / 2; k++) {
            candidate_palindrome[n - 1 - k] = candidate_palindrome[k];
        }

        // --- Step 2: Compare the candidate palindrome with the original number ---
        // If the candidate palindrome is strictly greater than the original number,
        // then this candidate is the next palindrome.
        // Python's list comparison works lexicographically, which is equivalent to numerical comparison for digit lists.
        if (compareArrays(candidate_palindrome, current_digits) > 0) {
            return Arrays.toString(candidate_palindrome);
        }

        // --- Step 3: If the candidate palindrome is not greater (i.e., smaller or equal),
        // then we need to increment the left half of the original number and then mirror again. ---
        // This is the logic that was always executed in the buggy code. Now, it's conditional.

        // Start incrementing from the middle-left digit.
        int i = mid_idx;
        int carry = 1; // Start with a carry of 1 to increment the number

        // Propagate carry leftwards from the center of the number (or the middle of the left half).
        // The loop iterates as long as we have digits to process on the left side
        // and there's still a carry to propagate.
        while (i >= 0 && carry > 0) {
            int current_sum = current_digits[i] + carry;
            current_digits[i] = current_sum % 10;
            carry = current_sum / 10;
            i--; // Move left to propagate carry to the next digit
        }

        // If after the loop, carry is still 1, it means all digits were 9s (e.g., [9,9] or [9,9,9]).
        // In this case, the next palindrome is 1 followed by (n-1) zeros and a 1.
        // This handles cases like [9,9] -> [1,0,1] or [9,9,9] -> [1,0,0,1]
        if (carry == 1) {
            // This means the number was like [9,9] or [9,9,9] and incrementing
            // the left half resulted in all zeros and a carry out.
            // The next palindrome will have an increased length.
            int[] result = new int[n + 1];
            result[0] = 1;
            // The elements from result[1] to result[n-1] are already 0 by default for int arrays
            result[n] = 1;
            return Arrays.toString(result);
        }

        // If not all 9s (i.e., carry is 0), the left half (and potentially the middle digit for odd n)
        // of the current_digits list has been incremented and carries propagated.
        // Now, mirror this modified left half to the right half to form the complete palindrome.
        for (int k = 0; k < n / 2; k++) {
            current_digits[n - 1 - k] = current_digits[k];
        }

        return Arrays.toString(current_digits);
    }
}