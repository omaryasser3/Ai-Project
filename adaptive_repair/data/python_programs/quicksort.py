def quicksort(arr):
    """
    Sorts a list of integers using the QuickSort algorithm.

    Optimized for better average-case performance and memory efficiency
    compared to the original implementation.

    Args:
        arr: A list of ints.

    Returns:
        A new list containing the elements of arr in sorted order.
    """
    if not arr:
        return []

    # Create a copy of the input array to perform in-place sorting.
    # This preserves the external behavior of the original function,
    # which returned a new sorted list rather than modifying the input.
    arr_copy = list(arr)
    _quicksort_inplace(arr_copy, 0, len(arr_copy) - 1)
    return arr_copy

def _quicksort_inplace(arr, low, high):
    """
    Helper function for in-place QuickSort.
    Recursively sorts the sub-array arr[low...high].
    """
    if low < high:
        # Partition the array and get the pivot's final position
        pivot_index = _partition(arr, low, high)

        # Recursively sort elements before and after the pivot
        _quicksort_inplace(arr, low, pivot_index - 1)
        _quicksort_inplace(arr, pivot_index + 1, high)

def _partition(arr, low, high):
    """
    Partitions the sub-array arr[low...high] around a pivot.
    Uses median-of-three pivot selection and Lomuto's partition scheme.
    """
    # Median-of-three pivot selection:
    # Choose the median of arr[low], arr[mid], arr[high] as the pivot.
    # This helps to avoid worst-case O(N^2) performance on already sorted
    # or reverse-sorted arrays.
    mid = (low + high) // 2

    # Sort arr[low], arr[mid], arr[high] to place the median at arr[high].
    # After these three swaps, arr[low] <= arr[mid] <= arr[high].
    if arr[low] > arr[mid]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[mid] > arr[high]:
        arr[mid], arr[high] = arr[high], arr[mid]

    # Now arr[mid] holds the median value. Swap it with arr[high]
    # so it can be used as the pivot for Lomuto's partition scheme.
    arr[mid], arr[high] = arr[high], arr[mid]

    pivot = arr[high] # The chosen pivot
    i = low - 1       # Index of smaller element

    # Iterate through elements from low to high-1
    for j in range(low, high):
        # If current element is smaller than or equal to the pivot
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i] # Swap arr[i] and arr[j]

    # Place the pivot element in its correct sorted position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1 # Return the partitioning index