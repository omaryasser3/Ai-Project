def lcs_length(s, t):
    from collections import Counter

    dp = Counter()
    max_len = 0 # Initialize max_len to track the maximum length found

    for i in range(len(s)):
        for j in range(len(t)):
            if s[i] == t[j]:
                # If characters match, extend the common substring from the previous diagonal position
                dp[i, j] = dp[i - 1, j - 1] + 1
                # Update max_len if the current common substring is longer
                if dp[i, j] > max_len:
                    max_len = dp[i, j]
            # If characters do not match, the common substring ending at s[i] and t[j] is 0.
            # Counter's default for non-existent keys is 0, so no explicit 'else' is needed here.

    return max_len



"""
Longest Common Substring
longest-common-substring

Input:
    s: a string
    t: a string

Output:
    Length of the longest substring common to s and t

Example:
    >>> lcs_length('witch', 'sandwich')
    2
    >>> lcs_length('meow', 'homeowner')
    4
"""
