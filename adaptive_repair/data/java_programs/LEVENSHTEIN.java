package java_programs;

public class LEVENSHTEIN {
    public static int levenshtein(String source, String target) {
        int m = source.length();
        int n = target.length();

        // Create a DP table to store results of subproblems.
        // dp[i][j] will be the Levenshtein distance between source[:i] and target[:j].
        int[][] dp = new int[m + 1][n + 1];

        // Base cases:
        // If source is empty, distance is length of target (all insertions).
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;
        }
        // If target is empty, distance is length of source (all deletions).
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;
        }

        // Fill the DP table using bottom-up approach.
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (source.charAt(i - 1) == target.charAt(j - 1)) {
                    // Characters match, no cost. Take the diagonal value.
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    // Characters don't match. Consider the minimum of three possibilities:
                    // 1. Insertion: dp[i][j-1] (insert target[j-1] into source[:i])
                    // 2. Deletion: dp[i-1][j] (delete source[i-1] from source[:i])
                    // 3. Substitution: dp[i-1][j-1] (substitute source[i-1] with target[j-1])
                    dp[i][j] = 1 + Math.min(dp[i][j - 1], Math.min(dp[i - 1][j], dp[i - 1][j - 1]));
                }
            }
        }

        return dp[m][n];
    }
}