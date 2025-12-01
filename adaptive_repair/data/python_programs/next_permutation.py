def next_permutation(perm):
    for i in range(len(perm) - 2, -1, -1):
        if perm[i] < perm[i + 1]:
            # Found the pivot 'i'. Now find the smallest element in the suffix perm[i+1:]
            # that is greater than perm[i]. Since perm[i+1:] is in descending order,
            # iterating from right to left and finding the first element perm[j] such
            # that perm[j] > perm[i] will correctly identify this element.
            for j in range(len(perm) - 1, i, -1):
                if perm[j] > perm[i]:  # BUG FIX: Changed condition from < to >
                    next_perm = list(perm)
                    next_perm[i], next_perm[j] = next_perm[j], next_perm[i]
                    # After swapping, the suffix perm[i+1:] needs to be sorted in ascending order.
                    # Since it was in descending order before the swap, reversing it achieves this.
                    next_perm[i + 1:] = list(reversed(next_perm[i + 1:])) # Ensure slice assignment uses a list
                    return next_perm
    # According to the precondition, this part should not be reached.
    # If it were, it would mean the input perm is sorted in reverse order,
    # and the next permutation would be the sorted (ascending) list.
    return None # Or raise an error, or return sorted(perm) if precondition was relaxed.


"""
Next Permutation
next-perm


Input:
    perm: A list of unique ints

Precondition:
    perm is not sorted in reverse order

Output:
    The lexicographically next permutation of the elements of perm

Example:
    >>> next_permutation([3, 2, 4, 1])
    [3, 4, 1, 2]
"""