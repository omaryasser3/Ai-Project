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
public class FLATTEN {
    public static Object flatten(Object arr) {
        if (arr instanceof ArrayList) {
            ArrayList narr = (ArrayList) arr;
            ArrayList result = new ArrayList();
            for (Object x : narr) {
                // Recursively flatten each element. 
                // The flatten(x) call will now always return an ArrayList 
                // (either a flattened sublist or a single-element list for non-lists).
                // We then add all elements from this returned list to our result.
                result.addAll((ArrayList) flatten(x));
            }
            return result;
        } else {
            // Base case: If 'arr' is not an ArrayList (e.g., Integer, String, null), 
            // it's a leaf element that should be part of the flattened list.
            // Wrap it in a new ArrayList to maintain a consistent return type 
            // (as the main branch always returns an ArrayList) and to allow 
            // 'addAll' to be used uniformly in the recursive step.
            ArrayList singleElementList = new ArrayList();
            singleElementList.add(arr);
            return singleElementList;
        }
    }
}