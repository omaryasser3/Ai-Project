package java_programs;

import java.util.Queue;
import java.util.LinkedList;
import java.util.Set;
import java.util.HashSet;
import java.util.List;

interface GraphNode<T> {
    List<T> getSuccessors();
}

public class BREADTH_FIRST_SEARCH {

    public static <T extends GraphNode<T>> boolean breadth_first_search(T startNode, T goalNode) {
        Set<T> nodesVisited = new HashSet<>();
        Queue<T> queue = new LinkedList<>();

        queue.offer(startNode);
        nodesVisited.add(startNode);

        while (!queue.isEmpty()) {
            T node = queue.poll();

            if (node.equals(goalNode)) {
                return true;
            } else {
                for (T successorNode : node.getSuccessors()) {
                    if (!nodesVisited.contains(successorNode)) {
                        queue.offer(successorNode);
                        nodesVisited.add(successorNode);
                    }
                }
            }
        }
        return false;
    }
}