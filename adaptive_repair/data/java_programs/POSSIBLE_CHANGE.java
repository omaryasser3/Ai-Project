package java_programs;

public class POSSIBLE_CHANGE {
    public static int possible_change(int[] coins, int total) {
        // Handle edge case for negative total
        if (total < 0) {
            return 0;
        }

        // dp[i] will store the number of ways to make amount i
        // Initialize dp array with zeros, size total + 1
        int[] dp = new int[total + 1];

        // Base case: There is one way to make amount 0 (by using no coins)
        dp[0] = 1;

        // Iterate through each coin denomination
        for (int coin : coins) {
            // For each coin, update the dp array for amounts from 'coin' up to 'total'
            // This ensures that each coin is considered for all possible amounts it can contribute to.
            for (int i = coin; i <= total; i++) {
                // Add the number of ways to make the remaining amount (i - coin)
                // This represents using the current 'coin' to reach amount 'i'.
                dp[i] += dp[i - coin];
            }
        }

        // The final result is the number of ways to make the 'total' amount
        return dp[total];
    }
}