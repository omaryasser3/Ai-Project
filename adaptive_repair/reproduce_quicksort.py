from data.python_programs.quicksort import quicksort

def test_quicksort():
    # Test case with duplicates
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    sorted_arr = quicksort(arr)
    expected = sorted(arr)
    
    print(f"Original: {arr}")
    print(f"Sorted:   {sorted_arr}")
    print(f"Expected: {expected}")
    
    assert sorted_arr == expected, "Quicksort failed to sort correctly (likely dropped duplicates)"
    print("Test passed!")

if __name__ == "__main__":
    try:
        test_quicksort()
    except AssertionError as e:
        print(f"Assertion Error: {e}")
