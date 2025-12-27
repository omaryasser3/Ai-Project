package java_programs;
import java.util.*;
import java.util.ArrayDeque;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * @author derricklin
 */
public class BREADTH_FIRST_SEARCH {

    public static boolean breadth_first_search(Node startnode, Node goalnode) {
        Deque<Node> queue = new ArrayDeque<>();
        queue.addLast(startnode);

        Set<Node> nodesvisited = new HashSet<>();
        nodesvisited.add(startnode);

        while (!queue.isEmpty()) {
            Node node = queue.removeFirst();

            if (node == goalnode) {
                return true;
            } else {
                for (Node successor_node : node.getSuccessors()) {
                    if (!nodesvisited.contains(successor_node)) {
                        // For a standard Breadth-First Search, successors are added
                        // to the end of the queue (addLast) to maintain FIFO order.
                        queue.addLast(successor_node);
                        nodesvisited.add(successor_node);
                    }
                }
            }
        }
        // If the loop finishes, it means the queue is empty and the goalnode was not found.
        // Therefore, the goalnode is unreachable from the startnode.
        return false;
    }

}