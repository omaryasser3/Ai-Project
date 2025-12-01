def levenshtein(source, target):
    m = len(source)
    n = len(target)

    # Create a DP table to store results of subproblems.
    # dp[i][j] will store the Levenshtein distance between source[:i] and target[:j].
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize the first row and first column.
    # If source is empty, the distance to target[:j] is j (insert j characters).
    for j in range(n + 1):
        dp[0][j] = j
    # If target is empty, the distance from source[:i] is i (delete i characters).
    for i in range(m + 1):
        dp[i][0] = i

    # Fill the DP table using a bottom-up approach.
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if source[i-1] == target[j-1]:
                # Characters match, no operation needed for this pair.
                # The distance is the same as the distance of the prefixes without these characters.
                dp[i][j] = dp[i-1][j-1]
            else:
                # Characters don't match, consider the cost of three possible operations:
                # 1. Deletion: delete source[i-1] -> dp[i-1][j] + 1
                # 2. Insertion: insert target[j-1] into source -> dp[i][j-1] + 1
                # 3. Substitution: substitute source[i-1] with target[j-1] -> dp[i-1][j-1] + 1
                # We take the minimum of these costs.
                dp[i][j] = 1 + min(dp[i-1][j],      # Cost of deletion
                                   dp[i][j-1],      # Cost of insertion
                                   dp[i-1][j-1])    # Cost of substitution

    # The final result is the distance between the full source and target strings.
    return dp[m][n]
