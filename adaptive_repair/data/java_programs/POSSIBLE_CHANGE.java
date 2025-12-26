package java_programs;

public class POSSIBLE_CHANGE {

    public static int possible_change(int[] coins, int total) {
        // dp[i] will store the number of ways to make change for amount i.
        // Initialize dp array with zeros. The size is total + 1 to include amount 0 up
        // to total.
        int[] dp = new int[total + 1];

        // Base case: There is one way to make change for 0 (by using no coins).
        dp[0] = 1;

        // Iterate through each coin available.
        // The order of coins does not matter for the total number of ways.
        for (int coin : coins) {
            // For each coin, iterate from the coin's value up to the total amount.
            // This ensures that we consider using the current coin to make up the amount
            // and allows for multiple uses of the same coin.
            for (int j = coin; j <= total; j++) {
                // The number of ways to make change for amount j using the current set of coins
                // is the sum of:
                // 1. Ways to make change for j without using the current coin (already
                // accumulated in dp[j] from previous coin iterations).
                // 2. Ways to make change for j - coin, then adding the current coin (dp[j -
                // coin]).
                // This effectively adds all combinations that include the current coin at least
                // once.
                dp[j] += dp[j - coin];
            }
        }

        // The final result is the number of ways to make change for the 'total' amount.
        return dp[total];
    }
}