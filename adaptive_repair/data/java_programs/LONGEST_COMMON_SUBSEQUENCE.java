package java_programs;

public class LONGEST_COMMON_SUBSEQUENCE {

    public static String longestCommonSubsequence(String a, String b) {
        int m = a.length();
        int n = b.length();

        // dp[i][j] will store the length of the LCS of a[:i] and b[:j]
        // Initialize with zeros. dp[0][j] and dp[i][0] are 0 for empty prefixes.
        // Java initializes int arrays to 0 by default.
        int[][] dp = new int[m + 1][n + 1];

        // Fill the dp table
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) {
                    // If characters match, extend the LCS from the diagonal
                    dp[i][j] = 1 + dp[i - 1][j - 1];
                } else {
                    // If characters don't match, take the maximum LCS length from
                    // either skipping the current character in 'a' (dp[i-1][j])
                    // or skipping the current character in 'b' (dp[i][j-1])
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }

        // Reconstruct the LCS string by backtracking through the dp table
        StringBuilder lcsChars = new StringBuilder();
        int i = m;
        int j = n;
        while (i > 0 && j > 0) {
            if (a.charAt(i - 1) == b.charAt(j - 1)) {
                // If characters match, it means this character is part of the LCS.
                // Add it and move diagonally up-left.
                lcsChars.append(a.charAt(i - 1));
                i--;
                j--;
            } else if (dp[i - 1][j] > dp[i][j - 1]) {
                // If the LCS length came from dp[i-1][j], it means a[i-1] was not part of the LCS.
                // Move up (skip a[i-1]).
                i--;
            } else {
                // If the LCS length came from dp[i][j-1], it means b[j-1] was not part of the LCS.
                // Move left (skip b[j-1]).
                j--;
            }
        }

        // The LCS was built in reverse order during backtracking, so reverse it.
        return lcsChars.reverse().toString();
    }
}