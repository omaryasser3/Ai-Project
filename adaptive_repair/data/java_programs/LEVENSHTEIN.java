package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class LEVENSHTEIN {
    public static int levenshtein(String source, String target) {
        int m = source.length();
        int n = target.length();

        // Create a DP table to store results of subproblems.
        // dp[i][j] will store the Levenshtein distance between
        // the first i characters of 'source' and the first j characters of 'target'.
        int[][] dp = new int[m + 1][n + 1];

        // Initialize the DP table for base cases.
        // If source is empty, the distance is the length of target (all insertions).
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;
        }

        // If target is empty, the distance is the length of source (all deletions).
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;
        }

        // Fill the DP table iteratively.
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                // Calculate the cost for the current characters.
                // If characters match, cost is 0; otherwise, cost is 1.
                int cost = (source.charAt(i - 1) == target.charAt(j - 1)) ? 0 : 1;

                // The Levenshtein distance dp[i][j] is the minimum of three possibilities:
                // 1. Deletion: dp[i-1][j] + 1 (delete source.charAt(i-1))
                // 2. Insertion: dp[i][j-1] + 1 (insert target.charAt(j-1))
                // 3. Substitution/Match: dp[i-1][j-1] + cost (substitute source.charAt(i-1) for target.charAt(j-1) or match them)
                dp[i][j] = Math.min(dp[i - 1][j] + 1, // Deletion
                                 Math.min(dp[i][j - 1] + 1, // Insertion
                                          dp[i - 1][j - 1] + cost)); // Substitution or Match
            }
        }

        // The final result is the distance between the entire source and target strings.
        return dp[m][n];
    }
}