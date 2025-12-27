package java_programs;

import java.util.ArrayList;
import java.util.List;

public class POWERSET {

    public static List<List<Integer>> powerset(List<Integer> arr) {
        // Start the recursion from the beginning of the array (index 0)
        return _powerset_recursive(arr, 0);
    }

    private static List<List<Integer>> _powerset_recursive(List<Integer> arr, int currentIndex) {
        // Base case: When we've considered all elements up to the end of the array
        if (currentIndex == arr.size()) {
            // The powerset of an empty set (what's left after currentIndex) is a set containing an empty set: { {} }
            List<List<Integer>> baseCaseResult = new ArrayList<>();
            baseCaseResult.add(new ArrayList<>()); // Add an empty list
            return baseCaseResult;
        }

        // Get the current element to consider
        Integer firstElement = arr.get(currentIndex);

        // Recursively get all subsets of the 'rest' part of the array (elements from currentIndex + 1 onwards)
        List<List<Integer>> restSubsets = _powerset_recursive(arr, currentIndex + 1);

        List<List<Integer>> output = new ArrayList<>();
        for (List<Integer> subset : restSubsets) {
            // 1. Include the subset itself. These are the subsets that do NOT contain 'firstElement'.
            // We add a new ArrayList instance to ensure subsets are distinct objects,
            // preventing modification of one from affecting others.
            output.add(new ArrayList<>(subset)); 

            // 2. Create a new subset by adding 'firstElement' to the current subset.
            // These are the subsets that DO contain 'firstElement'.
            List<Integer> subsetWithFirstElement = new ArrayList<>();
            subsetWithFirstElement.add(firstElement); // Add the current element
            subsetWithFirstElement.addAll(subset);    // Add all elements from the existing subset
            output.add(subsetWithFirstElement);
        }

        return output;
    }
}