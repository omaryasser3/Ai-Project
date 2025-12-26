package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * @author derricklin
 */
public class HANOI {
    // default start=1, end=3
    public static List<Pair<Integer,Integer>> hanoi(int height, int start, int end) {
        ArrayList<Pair<Integer,Integer>> steps = new ArrayList<Pair<Integer,Integer>>();

        if (height > 0) {
            PriorityQueue<Integer> crap_set = new PriorityQueue<Integer>();
            crap_set.add(1);
            crap_set.add(2);
            crap_set.add(3);
            crap_set.remove(start);
            crap_set.remove(end);
            int helper = crap_set.poll(); // This is the auxiliary peg

            // Step 1: Move height-1 disks from 'start' to 'helper' using 'end' as auxiliary
            steps.addAll(hanoi(height-1, start, helper));
            
            // Step 2: Move the largest disk (height-th disk) from 'start' to 'end'
            // BUG FIX: The largest disk should move directly from 'start' to 'end'.
            // It was incorrectly moving from 'start' to 'helper'.
            steps.add(new Pair<Integer,Integer>(start, end)); 
            
            // Step 3: Move height-1 disks from 'helper' to 'end' using 'start' as auxiliary
            steps.addAll(hanoi(height-1, helper, end));
        }

        return steps;
    }


    public static class Pair<F, S> {
        private F first; //first member of pair
        private S second; //second member of pair

        public Pair(F first, S second) {
            this.first = first;
            this.second = second;
        }

        public void setFirst(F first) {
            this.first = first;
        }

        public void setSecond(S second) {
            this.second = second;
        }

        public F getFirst() {
            return first;
        }

        public S getSecond() {
            return second;
        }

        @Override
        public String toString() {
            return "(" + String.valueOf(first) + ", " + String.valueOf(second) + ")";
        }
    }
}