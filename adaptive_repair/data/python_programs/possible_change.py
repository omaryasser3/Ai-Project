import functools

def possible_change(coins, total):
    # Sort coins to ensure consistent order. While not strictly necessary for correctness
    # with this specific memoized recursive approach (as the index handles the coin identity),
    # it's good practice for dynamic programming problems. It ensures that if the input
    # `coins` list order changes, the internal behavior (and thus cache hits) remains consistent.
    coins = sorted(coins)

    @functools.lru_cache(None)  # Cache all results of this function
    def _possible_change_memo(idx, current_total):
        # Base case 1: If the total is 0, we've found one way (by using no more coins).
        if current_total == 0:
            return 1
        # Base case 2: If the total is negative, this path is invalid.
        if current_total < 0:
            return 0
        
        # Base case 3: If we've run out of coin denominations to consider
        # (idx has reached or exceeded the length of the coins list)
        # and the total is still positive, it's impossible to make change.
        if idx == len(coins):
            return 0

        # Recursive step:
        # We have two choices for the current coin (coins[idx]):

        # Choice 1: Include the current coin.
        # Subtract its value from the total and recursively call with the same coin index,
        # as we can use the same coin multiple times.
        ways_with_current_coin = _possible_change_memo(idx, current_total - coins[idx])

        # Choice 2: Exclude the current coin.
        # Move to the next coin denomination (idx + 1) without using the current one.
        ways_without_current_coin = _possible_change_memo(idx + 1, current_total)

        # The total number of ways is the sum of ways from these two choices.
        return ways_with_current_coin + ways_without_current_coin

    # Start the recursion from the first coin (index 0) and the given total.
    return _possible_change_memo(0, total)
