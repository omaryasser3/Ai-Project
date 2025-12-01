def possible_change(coins, total):
    # Initialize a DP table where dp[i] will store the number of ways to make change for amount i.
    # The size of the table is total + 1 to account for amounts from 0 to total.
    dp = [0] * (total + 1)

    # There is one way to make change for 0 (by using no coins).
    dp[0] = 1

    # Iterate through each coin denomination.
    # The order of loops (coins first, then amounts) is crucial for counting combinations
    # (where the order of coins used doesn't matter).
    for coin in coins:
        # For each coin, iterate from the coin's value up to the total amount.
        # This ensures that we consider using the current coin for each possible amount.
        for amount in range(coin, total + 1):
            # The number of ways to make 'amount' is the sum of:
            # 1. The ways to make 'amount' without using the current 'coin' (which is dp[amount] before this update).
            # 2. The ways to make 'amount - coin' using any of the coins considered so far (including the current 'coin'),
            #    and then adding the current 'coin' to those combinations.
            dp[amount] += dp[amount - coin]

    # The final result is the number of ways to make change for the 'total' amount.
    return dp[total]
