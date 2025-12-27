package java_programs;

public class NEXT_PERMUTATION {
    public static int[] next_permutation(int[] perm) {
        int n = perm.length;
        int i = n - 2;
        while (i >= 0 && perm[i] >= perm[i + 1]) {
            i--;
        }

        if (i == -1) {
            return null; // Equivalent to Python's [] to signal no next permutation
        }

        int j = n - 1;
        // Find the largest index j to the right of i such that perm[j] > perm[i].
        // Due to the descending order of perm[i+1:], this also finds the smallest value perm[j] > perm[i].
        while (j > i) {
            if (perm[j] > perm[i]) {
                break;
            }
            j--;
        }

        // Swap perm[i] and perm[j]
        int temp = perm[i];
        perm[i] = perm[j];
        perm[j] = temp;

        // Reverse the suffix in-place using two pointers to avoid creating new list objects
        int left = i + 1;
        int right = n - 1;
        while (left < right) {
            // Swap perm[left] and perm[right]
            temp = perm[left];
            perm[left] = perm[right];
            perm[right] = temp;
            left++;
            right--;
        }

        return perm;
    }
}