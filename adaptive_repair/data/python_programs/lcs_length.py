def lcs_length(s, t):
    from collections import Counter

    dp = Counter() # Stores the length of the common suffix ending at s[i] and t[j]
    max_len = 0    # Tracks the maximum length found across all dp[i, j]

    for i in range(len(s)):
        for j in range(len(t)):
            if s[i] == t[j]:
                # If characters match, extend the common substring from the diagonal element.
                # dp[i-1, j-1] represents the length of the common substring ending at s[i-1] and t[j-1].
                # Counter handles negative indices (e.g., dp[-1,-1]) by returning 0, which is correct for base cases.
                dp[i, j] = dp[i - 1, j - 1] + 1
                # Update the overall maximum length found so far.
                if dp[i, j] > max_len:
                    max_len = dp[i, j]
            # If characters do not match (s[i] != t[j]), the common substring ending at s[i] and t[j]
            # must reset to 0. Counter's default behavior ensures dp[i, j] remains 0 if not explicitly assigned.

    return max_len