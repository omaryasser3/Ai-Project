from .node import Node
from .detect_cycle import detect_cycle


"""
Driver to test reverse linked list
"""
def main():
    # Case 1: 5-node list input with no cycle
    # Expected Output: Cycle not detected!
    node1_c1 = Node(1)
    node2_c1 = Node(2, node1_c1)
    node3_c1 = Node(3, node2_c1)
    node4_c1 = Node(4, node3_c1)
    node5_c1 = Node(5, node4_c1) # Head: 5 -> 4 -> 3 -> 2 -> 1

    if detect_cycle(node5_c1):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 2: 5-node list input with cycle
    # Expected Output: Cycle detected!
    # Recreate the 5-node list for isolation
    node1_c2 = Node(1)
    node2_c2 = Node(2, node1_c2)
    node3_c2 = Node(3, node2_c2)
    node4_c2 = Node(4, node3_c2)
    node5_c2 = Node(5, node4_c2) # Head: 5 -> 4 -> 3 -> 2 -> 1
    node1_c2.successor = node5_c2 # Create cycle: 5 -> 4 -> 3 -> 2 -> 1 -> 5

    if detect_cycle(node5_c2):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 3: 2-node list with cycle
    # Expected Output: Cycle detected!
    # Create new nodes for a 2-node list
    node_a_c3 = Node(10)
    node_b_c3 = Node(11, node_a_c3) # Head: 11 -> 10
    node_a_c3.successor = node_b_c3 # Create cycle: 11 -> 10 -> 11

    if detect_cycle(node_b_c3):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 4: 2-node list with no cycle
    # Expected Output: Cycle not detected!
    # This case was already isolated.
    node6_c4 = Node(6)
    node7_c4 = Node(7, node6_c4) # Head: 7 -> 6

    if detect_cycle(node7_c4):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 5: 1-node list
    # Expected Output: Cycle not detected!
    # This case was already isolated.
    node_c5 = Node(0)

    if detect_cycle(node_c5):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 6: 5 nodes in total. the last 2 nodes form a cycle. input the first node
    # Expected Output: Cycle detected!
    # Create a completely new 5-node list for this case
    node_e_c6 = Node(50)
    node_d_c6 = Node(40, node_e_c6)
    node_c_c6 = Node(30, node_d_c6)
    node_b_c6 = Node(20, node_c_c6)
    node_a_c6 = Node(10, node_b_c6) # Head: 10 -> 20 -> 30 -> 40 -> 50

    # Create the cycle: the last node (node_e_c6) points to the second to last (node_d_c6)
    node_e_c6.successor = node_d_c6 # Cycle: 50 -> 40 -> 50
    # Full list: 10 -> 20 -> 30 -> 40 -> 50 -> 40 (cycle)

    if detect_cycle(node_a_c6):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()


if __name__ == "__main__":
    main()
