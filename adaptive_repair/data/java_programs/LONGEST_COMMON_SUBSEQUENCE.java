package java_programs;

public class LONGEST_COMMON_SUBSEQUENCE {

    private static String[][] memo;
    private static String strA;
    private static String strB;
    private static int lenA;
    private static int lenB;

    public static String longest_common_subsequence(String a, String b) {
        strA = a;
        strB = b;
        lenA = a.length();
        lenB = b.length();

        // Initialize memoization table.
        // The size is (lenA + 1) x (lenB + 1) because indices go up to lenA and lenB,
        // and we need to store results for (lenA, j) and (i, lenB) as base cases.
        memo = new String[lenA + 1][lenB + 1];

        return _lcs(0, 0);
    }

    private static String _lcs(int i, int j) {
        // Check if the result for this subproblem (i, j) has already been computed.
        if (memo[i][j] != null) {
            return memo[i][j];
        }

        // Base case: if either string segment is exhausted, there's no common subsequence.
        // Return an empty string.
        if (i == lenA || j == lenB) {
            return "";
        }

        String result;
        // If the current characters from both strings match, they are part of the LCS.
        // Append the character and recurse for the rest of the strings (i+1, j+1).
        if (strA.charAt(i) == strB.charAt(j)) {
            result = strA.charAt(i) + _lcs(i + 1, j + 1);
        } else {
            // If characters don't match, explore two possibilities:
            // 1. Skip the current character in string B (move to B[j+1])
            // 2. Skip the current character in string A (move to A[i+1])
            // Take the longer of the two resulting LCSs.
            String lcs1 = _lcs(i, j + 1); // LCS when A[i] is considered, but B[j] is skipped
            String lcs2 = _lcs(i + 1, j); // LCS when B[j] is considered, but A[i] is skipped
            result = (lcs1.length() >= lcs2.length()) ? lcs1 : lcs2;
        }

        // Store the computed result in the memoization table before returning,
        // so it can be reused if this subproblem is encountered again.
        memo[i][j] = result;
        return result;
    }
}