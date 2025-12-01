def max_sublist_sum(arr):
    max_ending_here = 0
    max_so_far = 0

    for x in arr:
        # Kadane's algorithm: At each element, decide whether to extend the current sublist
        # or start a new sublist with the current element itself. If adding 'x' to
        # 'max_ending_here' results in a sum less than 'x' itself, it means the previous
        # sublist sum was negative and detrimental, so it's better to start a new sublist from 'x'.
        max_ending_here = max(x, max_ending_here + x)
        
        # Update the overall maximum sum found so far
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far