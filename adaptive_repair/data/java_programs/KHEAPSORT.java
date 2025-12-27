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
public class KHEAPSORT {
    // import heapq
    // heap is data structure used for priority queue
    // pq O(log n) to pull off lowest priority item
    // heap is a type of binary tree
    // every node its value smaller than everything below it
    // priority queue in java is least-value first (at head)

    public static ArrayList<Integer> kheapsort(ArrayList<Integer> arr, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<Integer>();
        
        // Initialize the heap with the first 'k' elements.
        // This loop adds elements from index 0 up to k-1 (or arr.size()-1 if arr is smaller than k).
        for (int i = 0; i < k && i < arr.size(); i++) {
            heap.add(arr.get(i));
        }

        ArrayList<Integer> output = new ArrayList<Integer>();
        
        // Add the remaining elements from index 'k' onwards to the heap.
        // The original code would add an element and immediately poll one. This approach
        // is suitable for sorting a k-sorted array (where elements are 'k' positions away
        // from their sorted place) but not a general unsorted array, as it doesn't guarantee
        // the globally smallest element is always polled.
        // To ensure a fully sorted output for any array, all elements must be added to the heap
        // before any are extracted for the final sorted list.
        for (int i = k; i < arr.size(); i++) {
            heap.add(arr.get(i));
            // The original lines 'Integer popped = heap.poll();' and 'output.add(popped);'
            // were removed from this loop. Polling is now deferred until all elements are in the heap.
        }

        // After all elements from the input array have been added to the heap,
        // drain the heap to get the elements in sorted order.
        while (!heap.isEmpty()) {
            output.add(heap.poll());
        }

        return output;

    }
}