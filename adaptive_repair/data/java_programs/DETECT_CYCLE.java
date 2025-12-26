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
public class DETECT_CYCLE {
    public static boolean detect_cycle(Node node) {
        // Handle edge cases: an empty list or a list with only one node.
        // In these scenarios, no cycle can exist, and attempting to access
        // successors would lead to NullPointerExceptions.
        if (node == null || node.getSuccessor() == null) {
            return false;
        }

        Node hare = node;
        Node tortoise = node;

        while (true) {
            // Tortoise moves one step.
            tortoise = tortoise.getSuccessor();
            // If tortoise becomes null, it means we reached the end of the list.
            // No cycle.
            if (tortoise == null) {
                return false;
            }

            // Hare moves two steps. Each step must be guarded against null.
            // First step for hare:
            if (hare.getSuccessor() == null) {
                return false; // Reached end of list, no cycle.
            }
            hare = hare.getSuccessor(); // Hare takes the first step.

            // Second step for hare:
            if (hare.getSuccessor() == null) {
                return false; // Reached end of list, no cycle.
            }
            hare = hare.getSuccessor(); // Hare takes the second step.

            // If hare and tortoise meet, a cycle is detected.
            if (hare == tortoise) {
                return true;
            }
        }
    }
}