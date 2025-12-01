import random

def kth(arr, k):
    """
    QuickSelect: Finds the k-th smallest element in an array in-place.
    This is an efficient equivalent to sorted(arr)[k].

    Input:
        arr: A list of ints (modified in-place)
        k: An int (0-based index)

    Precondition:
        0 <= k < len(arr)

    Output:
        The kth-lowest element of arr (0-based)
    """
    if not arr:
        raise ValueError("Input array cannot be empty.")
    if not (0 <= k < len(arr)):
        raise IndexError(f"k ({k}) is out of bounds for array of length {len(arr)}")

    # QuickSelect modifies the array in-place. If the original array
    # should not be modified, a copy should be made here:
    # arr_copy = list(arr)
    # return _kth_in_place(arr_copy, k, 0, len(arr_copy) - 1)

    return _kth_in_place(arr, k, 0, len(arr) - 1)

def _kth_in_place(arr, k, left, right):
    # Base case: If the sub-array has only one element, it must be the k-th element.
    if left == right:
        return arr[left]

    # Choose a random pivot index to ensure average O(N) performance
    # and avoid worst-case O(N^2) on pathological inputs (e.g., already sorted arrays).
    # Move the chosen pivot to the 'left' position to simplify the 3-way partition logic.
    pivot_idx = random.randint(left, right)
    arr[left], arr[pivot_idx] = arr[pivot_idx], arr[left]
    pivot_value = arr[left]

    # 3-way partition (Dijkstra's Dutch National Flag problem variant)
    # This partitions arr[left...right] into three sections:
    # 1. Elements < pivot_value (from arr[left] to arr[lt-1])
    # 2. Elements == pivot_value (from arr[lt] to arr[gt])
    # 3. Elements > pivot_value (from arr[gt+1] to arr[right])
    lt = left  # Pointer for the end of the 'less than' section
    gt = right # Pointer for the start of the 'greater than' section
    i = left + 1 # Current element being examined

    while i <= gt:
        if arr[i] < pivot_value:
            arr[i], arr[lt] = arr[lt], arr[i]
            lt += 1
            i += 1
        elif arr[i] > pivot_value:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
            # Note: i is NOT incremented here because the element swapped
            # into arr[i] from arr[gt] needs to be re-evaluated.
        else: # arr[i] == pivot_value
            i += 1

    # After partitioning, determine which section contains the k-th element.
    # 'k' is the 0-based global index we are searching for.

    if k < lt:
        # The k-th element is in the 'less than' partition.
        # Recurse on the sub-array arr[left ... lt-1].
        return _kth_in_place(arr, k, left, lt - 1)
    elif k > gt:
        # The k-th element is in the 'greater than' partition.
        # Recurse on the sub-array arr[gt+1 ... right].
        return _kth_in_place(arr, k, gt + 1, right)
    else:
        # The k-th element is within the 'equal to pivot' partition (arr[lt ... gt]).
        # Since all elements in this partition are equal to pivot_value,
        # the k-th element must be pivot_value.
        return pivot_value