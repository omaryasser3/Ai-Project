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
        ArrayList<Integer> middle = new ArrayList<Integer>(); // This list will hold the pivot and elements equal to it

        middle.add(pivot); // Add the initial pivot to the middle list

        // Iterate through the rest of the elements (excluding the first one, which is the pivot)
        for (Integer x : arr.subList(1, arr.size())) {
            if (x < pivot) {
                lesser.add(x);
            } else if (x > pivot) {
                greater.add(x);
            } else { // x == pivot
                middle.add(x); // Add elements equal to the pivot to the middle list
            }
        }
        
        lesser = quicksort(lesser);
        greater = quicksort(greater);
        
        // Combine the sorted lists: lesser + middle + greater
        // The original assembly logic (middle.addAll(greater); lesser.addAll(middle);) correctly concatenates
        // the three partitions in the right order if 'middle' contains all pivot-equal elements.
        middle.addAll(greater);
        lesser.addAll(middle);
        return lesser;

    }
}