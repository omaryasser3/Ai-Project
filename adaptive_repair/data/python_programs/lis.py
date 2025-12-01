import bisect

def lis(arr):
    # 'tails' is an array where tails[k] stores the smallest ending element
    # of an increasing subsequence of length k+1. For example, if tails[0] = 1,
    # it means there's an increasing subsequence of length 1 ending with 1.
    # If tails[1] = 3, it means there's an increasing subsequence of length 2 ending with 3.
    # The 'tails' array is always kept sorted in increasing order.
    tails = []

    for num in arr:
        # Use binary search to find the appropriate position for 'num' in 'tails'.
        # bisect_left returns an insertion point 'idx' such that all elements
        # in tails[:idx] are less than 'num', and all elements in tails[idx:]
        # are greater than or equal to 'num'.
        idx = bisect.bisect_left(tails, num)

        if idx == len(tails):
            # If 'idx' is equal to the current length of 'tails', it means 'num'
            # is greater than all elements currently in 'tails'. This implies 'num'
            # can extend the longest increasing subsequence found so far by one element.
            # So, we append 'num' to 'tails', effectively creating a new longest subsequence.
            tails.append(num)
        else:
            # Otherwise, 'num' is not greater than all elements in 'tails'.
            # 'tails[idx]' is the smallest element in 'tails' that is >= 'num'.
            # By replacing 'tails[idx]' with 'num', we are saying that we found an
            # increasing subsequence of length 'idx + 1' that ends with 'num'.
            # Since 'num' <= 'tails[idx]', this new subsequence ends with a smaller
            # or equal value. A smaller ending value for a subsequence of a given length
            # is always preferable, as it provides more opportunities for future elements
            # to extend it. This operation maintains the sorted property of 'tails'.
            tails[idx] = num

    # The final length of the 'tails' array is the length of the Longest Increasing Subsequence.
    return len(tails)