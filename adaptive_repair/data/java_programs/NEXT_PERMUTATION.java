package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * @author derricklin
 */
public class NEXT_PERMUTATION {
    public static ArrayList<Integer> next_permutation(ArrayList<Integer> perm) {
        // Step 1: Find the largest index `i` such that `perm[i] < perm[i+1]`.
        // If no such index exists, the permutation is the last permutation.
        for (int i = perm.size() - 2; i != -1; i--) {
            if (perm.get(i) < perm.get(i + 1)) {
                // Step 2: Find the largest index `j` such that `perm[j] > perm[i]`.
                // This `j` must be in the suffix `perm[i+1...]`.
                for (int j = perm.size() - 1; j != i; j--) {
                    // The issue description states the condition `perm.get(j) < perm.get(i)` was incorrect.
                    // The provided 'Buggy code' already contains the correct condition `perm.get(j) > perm.get(i)`.
                    if (perm.get(j) > perm.get(i)) { // This condition is already correct as per the algorithm.
                        // Step 3: Swap `perm[i]` and `perm[j]`.
                        // The original code used `next_perm = perm;` which implies
                        // modifying `perm` in place. We continue this behavior.
                        int temp_i = perm.get(i);
                        int temp_j = perm.get(j);
                        perm.set(i, temp_j);
                        perm.set(j, temp_i);

                        // Step 4: Reverse the suffix `perm[i+1...]`.
                        // Replaced the manual reversal with `Collections.reverse` for conciseness and efficiency.
                        Collections.reverse(perm.subList(i + 1, perm.size()));

                        return perm; // Return the modified permutation
                    }
                }
            }
        }

        // If the outer loop completes, it means no such `i` was found,
        // indicating that the input `perm` is the last permutation.
        // As per the original code's behavior, return an empty list.
        return new ArrayList<Integer>();
    }
}