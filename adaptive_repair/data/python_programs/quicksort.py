def quicksort(arr):
    # Handle empty or non-list input gracefully, matching original behavior for empty list
    if not arr:
        return []
    
    # Create a copy to preserve the original list and match the external behavior
    # of the original function, which returns a new sorted list.
    arr_copy = list(arr)
    
    _quicksort_recursive(arr_copy, 0, len(arr_copy) - 1)
    
    return arr_copy

def _quicksort_recursive(arr, low, high):
    if low < high:
        # pi is partitioning index, arr[pi] is now at right place
        pi = _partition(arr, low, high)

        # Separately sort elements before partition and after partition
        _quicksort_recursive(arr, low, pi - 1)
        _quicksort_recursive(arr, pi + 1, high)

def _partition(arr, low, high):
    # Choose the rightmost element as pivot
    pivot = arr[high]
    
    # Index of smaller element
    i = low - 1
    
    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            
    # Swap the pivot element with the element at i + 1
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1