package java_programs;

public class LCS_LENGTH {
    public static int lcs_length(String s, String t) {
        int m = s.length();
        int n = t.length();

        // Handle edge cases where one or both strings are empty
        if (m == 0 || n == 0) {
            return 0;
        }

        // dp[i][j] will store the length of the Longest Common Subsequence
        // of s[0...i-1] and t[0...j-1].
        // We use a 2D array.
        // The table size is (m+1) x (n+1) to simplify base cases.
        // Initialize all values to 0 (default for int arrays in Java).
        int[][] dp = new int[m + 1][n + 1];

        // Fill the dp table using 1-indexed loops for string characters
        // s.charAt(i-1) and t.charAt(j-1) correspond to the current characters
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (s.charAt(i - 1) == t.charAt(j - 1)) {
                    // If characters match, the LCS length is 1 plus the LCS of
                    // the prefixes s[0...i-2] and t[0...j-2].
                    dp[i][j] = 1 + dp[i - 1][j - 1];
                } else {
                    // If characters do not match, the LCS length is the maximum of:
                    // 1. LCS of s[0...i-2] and t[0...j-1]
                    // 2. LCS of s[0...i-1] and t[0...j-2]
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }

        // The length of the LCS for the entire strings s and t
        // is stored in the bottom-right cell of the dp table.
        return dp[m][n];
    }
}