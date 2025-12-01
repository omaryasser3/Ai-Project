import math

def max_sublist_sum(arr):
    # Handle empty array case: if the array is empty, the maximum sum is 0.
    # The original code would return 0 for an empty array, so we preserve this behavior.
    if not arr:
        return 0

    max_ending_here = 0
    # Initialize max_so_far to negative infinity. This is crucial for correctly handling
    # arrays where all numbers are negative. If initialized to 0, it would incorrectly
    # return 0 for such arrays, as any negative sum would be less than 0.
    max_so_far = -math.inf

    for x in arr:
        max_ending_here = max_ending_here + x
        
        # Update max_so_far with the maximum sum found so far. This step must occur
        # before potentially resetting max_ending_here to 0, to ensure that negative
        # sublist sums (which might be the maximum if all numbers are negative) are considered.
        max_so_far = max(max_so_far, max_ending_here)

        # If max_ending_here becomes negative, it means that the current sublist
        # ending at 'x' is detrimental to forming a larger sum. In this case,
        # we reset max_ending_here to 0, effectively starting a new sublist from the next element.
        if max_ending_here < 0:
            max_ending_here = 0

    return max_so_far