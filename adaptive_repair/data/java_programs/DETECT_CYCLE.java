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
        if (node == null) { // Handle empty list
            return false;
        }

        Node hare = node;
        Node tortoise = node;

        while (true) {
            // Tortoise moves one step
            tortoise = tortoise.getSuccessor();

            // Hare attempts to move two steps
            // Check if hare can move one step
            if (hare.getSuccessor() == null) {
                return false; // End of list reached, no cycle
            }
            // Store the result of the first step to check the second step
            Node hareNext = hare.getSuccessor();
            // Check if hare can move a second step
            if (hareNext.getSuccessor() == null) {
                return false; // End of list reached, no cycle
            }
            hare = hareNext.getSuccessor(); // Hare moves two steps

            if (hare == tortoise) {
                return true; // Cycle detected
            }
        }
    }
}