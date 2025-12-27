package java_programs;

import java.util.Arrays;

public class NEXT_PALINDROME {

    // Helper to convert digit array to a number string
    private static String listToStr(int[] lst) {
        StringBuilder sb = new StringBuilder();
        for (int digit : lst) {
            sb.append(digit);
        }
        return sb.toString();
    }

    public static String next_palindrome(int[] digitList) {
        int n = digitList.length;
        
        // Create a temporary array to work with, preserving the original for comparison
        int[] tempDigitList = Arrays.copyOf(digitList, n);
        
        // Find the middle point of the number
        int mid = n / 2;
        
        // Step 1: Generate a candidate palindrome by mirroring the left half
        // For example, for [1,2,3,4], left half is [1,2]. Mirroring gives [1,2,2,1].
        // For [1,2,3], left half is [1]. Middle is [2]. Mirroring gives [1,2,1].
        
        // Mirror the left half to the right half
        // The loop iterates from the leftmost digit of the left half up to (but not including) mid
        // and mirrors it to the corresponding position in the right half.
        for (int i = 0; i < mid; i++) {
            tempDigitList[n - 1 - i] = tempDigitList[i];
        }

        // Convert the original and the mirrored candidate to numbers for comparison
        String originalNumStr = listToStr(digitList);
        String candidateNumStr = listToStr(tempDigitList);

        // If the mirrored candidate is already greater than the original number,
        // then this candidate is the next palindrome.
        // Using string comparison for robustness with potentially large numbers.
        if (candidateNumStr.compareTo(originalNumStr) > 0) {
            return candidateNumStr;
        }
        
        // Step 2: If the mirrored candidate is not greater (i.e., it's smaller or equal),
        // we need to increment the "left half" of the number and then mirror it.
        
        // FIX: Re-initialize temp_digit_list to the original digits before incrementing.
        // The previous logic would increment the left half of the *candidate* palindrome
        // (which was already mirrored in Step 1). To correctly increment the "left half
        // of the number" as per the problem description's implied intent, we should
        // start from the original number's digits for the incrementing phase.
        tempDigitList = Arrays.copyOf(digitList, n);
        
        // Start incrementing from the rightmost digit of the left half (or the middle digit for odd length)
        // and propagate any carries to the left.
        
        // The index to start incrementing from.
        // For odd length, this is the middle digit.
        // For even length, this is the digit at mid - 1 (rightmost of the left half).
        int incrementStartIdx = mid - 1;
        int carry = 1;

        // If the number has an odd length, increment the middle digit first
        if (n % 2 == 1) {
            tempDigitList[mid] += carry;
            carry = tempDigitList[mid] / 10;
            tempDigitList[mid] %= 10;
        }
        
        // Propagate carry through the left half
        // We iterate from `incrementStartIdx` backwards to 0
        while (incrementStartIdx >= 0 && carry > 0) {
            tempDigitList[incrementStartIdx] += carry;
            carry = tempDigitList[incrementStartIdx] / 10;
            tempDigitList[incrementStartIdx] %= 10;
            incrementStartIdx--;
        }
        
        // After incrementing the left half (and potentially the middle digit),
        // check if there's a carry-out from the leftmost digit.
        // If carry is 1, it means the number of digits has increased (e.g., [9,9] -> "101", [9,9,9] -> "1001").
        // The next palindrome will have 1 at the start and end, with zeros in between.
        if (carry == 1) {
            StringBuilder sb = new StringBuilder();
            sb.append('1');
            for (int i = 0; i < n - 1; i++) {
                sb.append('0');
            }
            sb.append('1');
            return sb.toString();
        } else {
            // If no carry-out, mirror the new left half to the right half to form the final palindrome.
            for (int i = 0; i < mid; i++) {
                tempDigitList[n - 1 - i] = tempDigitList[i];
            }
                
            return listToStr(tempDigitList);
        }
    }
}