def pascal(n):
    if n == 0:
        return []

    rows = [[1]]

    for r in range(1, n):
        prev_row = rows[-1]
        current_row = [1]  # Each row starts with '1'

        # Calculate the inner elements of the current row
        # These are the sum of adjacent elements from the previous row.
        # The loop runs for (len(prev_row) - 1) times to get the middle elements.
        for i in range(len(prev_row) - 1):
            current_row.append(prev_row[i] + prev_row[i + 1])

        current_row.append(1)  # Each row ends with '1'
        rows.append(current_row)

    return rows