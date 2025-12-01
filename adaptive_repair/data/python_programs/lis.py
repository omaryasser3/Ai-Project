import bisect

def lis(arr):
    # 'tails' is a list where tails[i] stores the smallest ending element
    # of an increasing subsequence of length i+1. For example, tails[0] is
    # the smallest ending element of all LIS of length 1, tails[1] for length 2, etc.
    # The key property is that 'tails' is always sorted in increasing order.
    tails = []

    for val in arr:
        # Use binary search (bisect_left) to find the insertion point 'j' for 'val' in 'tails'.
        # 'j' represents the index where 'val' would fit to maintain sorted order.
        # This 'j' also corresponds to the length of the LIS that 'val' can extend or replace.
        # Specifically, if 'val' replaces tails[j], it forms an LIS of length j+1.
        j = bisect.bisect_left(tails, val)

        if j == len(tails):
            # If 'val' is greater than all elements in 'tails' (j is at the end),
            # it means 'val' can extend the longest increasing subsequence found so far.
            # We append 'val' to 'tails', effectively increasing the overall LIS length by one.
            tails.append(val)
        else:
            # If 'val' is not greater than all elements, it means we found an LIS
            # of length 'j+1' (represented by tails[j]) that ends with a value
            # greater than or equal to 'val'.
            # By replacing tails[j] with 'val', we get an LIS of the same length (j+1)
            # but with a smaller ending element. This is beneficial for future extensions
            # as a smaller ending element allows more subsequent numbers to potentially
            # extend this subsequence.
            tails[j] = val
            
    # The length of the 'tails' list is the length of the longest increasing subsequence.
    return len(tails)


"""
Longest Increasing Subsequence
longest-increasing-subsequence


Input:
    arr: A sequence of ints

Precondition:
    The ints in arr are unique

Output:
    The length of the longest monotonically increasing subsequence of arr

Example:
    >>> lis([4, 1, 5, 3, 7, 6, 2])
    3
"""
