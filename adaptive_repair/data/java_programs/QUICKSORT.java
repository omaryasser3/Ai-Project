package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class QUICKSORT {
    public static ArrayList<Integer> quicksort(ArrayList<Integer> arr) {
        if (arr.isEmpty()) {
            return new ArrayList<Integer>();
        }

        Integer pivot = arr.get(0);
        ArrayList<Integer> lesser = new ArrayList<Integer>();
        ArrayList<Integer> greater = new ArrayList<Integer>();
        ArrayList<Integer> middle = new ArrayList<Integer>(); // Initialize middle list

        // Add the chosen pivot to the middle list initially
        middle.add(pivot);

        // Partition the rest of the elements
        for (Integer x : arr.subList(1, arr.size())) {
            if (x < pivot) {
                lesser.add(x);
            } else if (x > pivot) {
                greater.add(x);
            } else { // x == pivot
                middle.add(x); // Elements equal to pivot go to the middle list
            }
        }
        
        // Recursively sort the lesser and greater partitions
        lesser = quicksort(lesser);
        greater = quicksort(greater);
        
        // Assemble the sorted lists: lesser + middle + greater
        lesser.addAll(middle);
        lesser.addAll(greater);
        
        return lesser;

    }
}