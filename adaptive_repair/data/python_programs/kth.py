import random

def _partition(arr, left, right, pivot_index):
    """
    Partitions the sub-array arr[left...right] around the pivot element.
    Moves elements smaller than the pivot to its left and larger elements to its right.
    Returns the final index of the pivot element.
    """
    pivot_value = arr[pivot_index]
    # Move pivot to the end of the sub-array for easier partitioning
    arr[pivot_index], arr[right] = arr[right], arr[pivot_index]
    store_index = left
    
    # Iterate through the sub-array, moving elements smaller than pivot to the left
    for i in range(left, right):
        if arr[i] < pivot_value:
            arr[store_index], arr[i] = arr[i], arr[store_index]
            store_index += 1
            
    # Move the pivot to its final sorted position
    arr[right], arr[store_index] = arr[store_index], arr[right]
    return store_index

def kth(arr, k):
    """
    QuickSelect

    This is an efficient equivalent to sorted(arr)[k].

    Input:
        arr: A list of ints
        k: An int

    Precondition:
        0 <= k < len(arr)

    Output:
        The kth-lowest element of arr (0-based)
    """
    if not (0 <= k < len(arr)):
        raise IndexError("k is out of bounds for array")
    if not arr: # Although precondition implies non-empty, a defensive check.
        raise ValueError("Input array cannot be empty")

    # Create a copy to preserve the external behavior of not modifying the original array.
    # The original implementation implicitly created copies with list comprehensions.
    arr_copy = list(arr)
    
    left, right = 0, len(arr_copy) - 1
    
    # Use an iterative approach to avoid Python's recursion depth limits
    # and improve performance by avoiding function call overhead for deep recursion.
    while True:
        # Select a random pivot to ensure average-case O(N) performance
        # and mitigate worst-case O(N^2) scenarios (e.g., sorted arrays).
        pivot_index = random.randint(left, right)
        
        # Partition the array in-place around the chosen pivot.
        # This avoids creating new lists, significantly reducing memory overhead.
        pivot_final_index = _partition(arr_copy, left, right, pivot_index)
        
        if k == pivot_final_index:
            return arr_copy[k]
        elif k < pivot_final_index:
            right = pivot_final_index - 1
        else: # k > pivot_final_index
            left = pivot_final_index + 1
