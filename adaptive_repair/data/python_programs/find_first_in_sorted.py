def find_first_in_sorted(arr, x):
    lo = 0
    hi = len(arr)  # hi is an exclusive upper bound

    ans = -1  # Stores the potential first index of x

    while lo < hi:  # Loop while the search space is valid
        mid = (lo + hi) // 2

        # Check if mid is a potential answer
        if arr[mid] == x:
            ans = mid  # Found a potential first occurrence
            hi = mid   # Try to find an even earlier occurrence in the left half
        elif arr[mid] < x:
            lo = mid + 1 # x must be in the right half
        else: # arr[mid] > x
            hi = mid     # x must be in the left half (or not present)

    return ans


"""
Fancy Binary Search
fancy-binsearch


Input:
    arr: A sorted list of ints
    x: A value to find

Output:
    The lowest index i such that arr[i] == x, or -1 if x not in arr

Example:
    >>> find_first_in_sorted([3, 4, 5, 5, 5, 5, 6], 5)
    2
"""