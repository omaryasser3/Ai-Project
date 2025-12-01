def find_first_in_sorted(arr, x):
    lo = 0
    hi = len(arr)

    # The loop condition must be 'lo < hi' because 'hi' is initialized as an exclusive upper bound (len(arr)).
    # Using 'lo <= hi' would allow 'mid' to potentially become 'len(arr)', leading to an IndexError
    # when 'arr[mid]' is accessed, especially for empty arrays or when 'x' is greater than all elements.
    while lo < hi:
        mid = (lo + hi) // 2

        if x == arr[mid] and (mid == 0 or x != arr[mid - 1]):
            return mid

        elif x <= arr[mid]:
            # If x is less than or equal to arr[mid], it means x could be at mid
            # or to its left. We narrow the search to the left half, including mid
            # as a potential candidate for the first occurrence. 'hi = mid' correctly
            # sets the new exclusive upper bound for the search space [lo, mid).
            hi = mid

        else:
            # If x is greater than arr[mid], it must be in the right half.
            # We exclude mid and search [mid + 1, hi).
            lo = mid + 1

    return -1