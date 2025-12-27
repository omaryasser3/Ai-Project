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
public class SUBSEQUENCES {
    public static ArrayList<ArrayList> subsequences(int a, int b, int k) {
        if (k == 0) {
            ArrayList<ArrayList> result = new ArrayList<>();
            result.add(new ArrayList()); // Add an empty list to represent the single empty subsequence
            return result;
        }

        ArrayList ret = new ArrayList(50);
        // The loop condition was incorrect, causing it to miss valid starting elements.
        // It should ensure that there are enough elements remaining (b - i) to form a subsequence of length k-1 after picking 'i'.
        // This means b - i >= k-1, which simplifies to i <= b - k + 1.
        // So, the loop should go up to b - k + 1 (inclusive), or i < b - k + 2.
        for (int i=a; i<b+2-k; i++) {
            for (ArrayList rest : subsequences(i+1, b, k-1)) {
                rest.add(0,i);
                ret.add(rest);
            }
        }

        return ret;
    }
}