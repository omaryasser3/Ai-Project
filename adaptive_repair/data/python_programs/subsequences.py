def subsequences(a, b, k):
    if k == 0:
        return [[]]

    ret = []
    # The numbers available are from 'a' up to 'b-1' (exclusive 'b').
    # To form a subsequence of length 'k', the first number 'i'
    # must be chosen such that there are 'k-1' numbers remaining
    # after 'i' up to 'b-1'.
    # The largest possible 'i' is (b-1) - (k-1) = b - k.
    # So, 'i' should iterate from 'a' up to 'b - k' (inclusive).
    # Python's range(start, stop) is exclusive of 'stop', so 'stop' should be 'b - k + 1'.
    for i in range(a, b - k + 1):
        ret.extend(
            [i] + rest for rest in subsequences(i + 1, b, k - 1)
        )

    return ret