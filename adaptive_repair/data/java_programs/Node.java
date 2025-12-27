package java_programs;
import java.util.*;

public class Node {

    private String value;
    private ArrayList<Node> successors;
    private ArrayList<Node> predecessors;
    // Removed: private Node successor; // This field was redundant and caused ambiguity

    public Node() {
        this.value = null;
        this.successors = new ArrayList<>();
        this.predecessors = new ArrayList<>();
    }

    public Node(String value) {
        this.value = value;
        this.successors = new ArrayList<>();
        this.predecessors = new ArrayList<>();
    }

    public Node(String value, Node successor) {
        this.value = value;
        this.predecessors = new ArrayList<>(); // Initialize predecessors to avoid null
        this.successors = new ArrayList<>(); // Initialize successors list to avoid null
        if (successor != null) {
            this.successors.add(successor); // Add it to the list, making the list the source of truth
        }
    }

    public Node(String value, ArrayList<Node> successors) {
        this.value = value;
        this.predecessors = new ArrayList<>(); // Initialize predecessors to avoid null
        // Handle null successors list gracefully by initializing to an empty list
        this.successors = (successors == null) ? new ArrayList<>() : successors;
    }

    public Node(String value, ArrayList<Node> predecessors, ArrayList<Node> successors) {
        this.value = value;
        // Handle null predecessors list gracefully
        this.predecessors = (predecessors == null) ? new ArrayList<>() : predecessors;
        // Handle null successors list gracefully
        this.successors = (successors == null) ? new ArrayList<>() : successors;
    }

    public String getValue() {
        return value;
    }

    public void setSuccessor(Node successor) {
        this.successors.clear(); // Clear the list of successors
        if (successor != null) {
            this.successors.add(successor); // Add the new single successor to the list
        }
    }

    public void setSuccessors(ArrayList<Node> successors) {
        // Handle null successors list gracefully
        this.successors = (successors == null) ? new ArrayList<>() : successors;
    }

    public void setPredecessors(ArrayList<Node> predecessors) {
        // Handle null predecessors list gracefully
        this.predecessors = (predecessors == null) ? new ArrayList<>() : predecessors;
    }

    public Node getSuccessor() {
        // Derive the "single successor" from the list of successors
        return this.successors.isEmpty() ? null : this.successors.get(0);
    }

    public ArrayList<Node> getSuccessors() {
        return successors;
    }
    public ArrayList<Node> getPredecessors() {
        return predecessors;
    }
}