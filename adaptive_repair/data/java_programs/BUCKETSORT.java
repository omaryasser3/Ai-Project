package java_programs;

import java.util.ArrayList;
import java.util.List;

public class BUCKETSORT {
    public static int[] bucketsort(int[] arr, int k) {
        int[] counts = new int[k];
        for (int x : arr) {
            counts[x] = counts[x] + 1;
        }

        List<Integer> sortedArrList = new ArrayList<>();
        // Iterate through the 'counts' array. The index 'value' represents the number
        // and 'frequency' represents how many times that number appeared in the original array.
        for (int value = 0; value < counts.length; value++) {
            int frequency = counts[value];
            for (int i = 0; i < frequency; i++) {
                sortedArrList.add(value);
            }
        }

        int[] sortedArr = new int[sortedArrList.size()];
        for (int i = 0; i < sortedArrList.size(); i++) {
            sortedArr[i] = sortedArrList.get(i);
        }

        return sortedArr;
    }
}