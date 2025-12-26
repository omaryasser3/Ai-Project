package java_programs;

import java.util.ArrayList;
import java.util.List;

public class POWERSET {

    public static <T> List<List<T>> powerset(List<T> arr) {
        // Base case: if the list is null or empty
        if (arr == null || arr.isEmpty()) {
            // The powerset of an empty set is a set containing only the empty set.
            List<List<T>> emptyPowerset = new ArrayList<>();
            emptyPowerset.add(new ArrayList<>());
            return emptyPowerset;
        } else {
            T first = arr.get(0);
            // Get the rest of the array by creating a new ArrayList from a subList view.
            // This mimics Python's slicing behavior (arr[1:]) which creates a new list,
            // avoiding modification of the original list and correctly representing the subproblem.
            List<T> rest = new ArrayList<>(arr.subList(1, arr.size()));
            List<List<T>> restSubsets = powerset(rest);

            List<List<T>> output = new ArrayList<>();
            // 1. Add all subsets from restSubsets (these are the subsets that do NOT contain 'first')
            output.addAll(restSubsets);

            // 2. For each subset in restSubsets, create a new subset by adding 'first' to it.
            for (List<T> subset : restSubsets) {
                // Create a new list for each new subset, combining 'first' with the current 'subset'.
                List<T> newSubsetWithFirst = new ArrayList<>();
                newSubsetWithFirst.add(first);
                newSubsetWithFirst.addAll(subset); // Add all elements from the current subset
                output.add(newSubsetWithFirst);
            }

            return output;
        }
    }
}