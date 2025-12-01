def longest_common_subsequence(a, b):
    # Use a dictionary to store results of subproblems (memoization table)
    # Keys will be tuples (index_a, index_b) representing the starting indices
    # of the substrings being considered (a[index_a:] and b[index_b:]).
    # Values will be the LCS string for those substrings.
    memo = {}

    def _lcs_recursive(i, j):
        # If this subproblem has already been solved, return the stored result
        if (i, j) in memo:
            return memo[(i, j)]

        # Base case: If either string (from its current index) is exhausted,
        # there's no common subsequence possible from this point onward.
        if i == len(a) or j == len(b):
            return ''

        # If the current characters at indices i and j match
        if a[i] == b[j]:
            # They are part of the LCS. Include a[i] (or b[j]) and
            # recursively find the LCS of the remaining parts of the strings.
            result = a[i] + _lcs_recursive(i + 1, j + 1)
        else:
            # If characters don't match, we have two choices:
            # 1. Skip the character from string 'a' (a[i]) and find LCS of a[i+1:] and b[j:]
            # 2. Skip the character from string 'b' (b[j]) and find LCS of a[i:] and b[j+1:]
            # We take the longer of the two results.
            result = max(
                _lcs_recursive(i, j + 1),    # Skip b[j]
                _lcs_recursive(i + 1, j),    # Skip a[i]
                key=len
            )

        # Store the computed result in the memoization table before returning
        # to avoid re-computation if this subproblem is encountered again.
        memo[(i, j)] = result
        return result

    # Start the recursive process from the beginning of both strings (indices 0, 0)
    return _lcs_recursive(0, 0)


"""
Longest Common Subsequence


Calculates the longest subsequence common to the two input strings. (A subsequence is any sequence of letters in the same order
they appear in the string, possibly skipping letters in between.)

Input:
    a: The first string to consider.
    b: The second string to consider.

Output:
    The longest string which is a subsequence of both strings. (If multiple subsequences of equal length exist, either is OK.)

Example:
    >>> longest_common_subsequence('headache', 'pentadactyl')
    'eadac'
"""