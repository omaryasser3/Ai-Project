package java_programs;

public class LCS_LENGTH {
    public static int lcs_length(String s, String t) {
        int m = s.length();
        int n = t.length();

        // Initialize dp table (m+1) x (n+1) with all zeros.
        // dp[i][j] will store the length of LCS of s[:i] and t[:j].
        // In Java, int arrays are initialized to 0 by default.
        int[][] dp = new int[m + 1][n + 1];

        // Fill the dp table
        // Iterate from 1 to m (inclusive) for string s
        for (int i = 1; i <= m; i++) {
            // Iterate from 1 to n (inclusive) for string t
            for (int j = 1; j <= n; j++) {
                // If characters match (s.charAt(i-1) and t.charAt(j-1) because s and t are 0-indexed)
                if (s.charAt(i - 1) == t.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                }
                // If characters do not match
                else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }

        // The length of the LCS of s and t is stored in dp[m][n]
        return dp[m][n];
    }
}