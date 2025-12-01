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
    node5_c1 = Node(5, node4_c1) # Head is node5_c1 (5 -> 4 -> 3 -> 2 -> 1)

    if detect_cycle(node5_c1):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 2: 5-node list input with cycle
    # Expected Output: Cycle detected!
    node1_c2 = Node(1)
    node2_c2 = Node(2, node1_c2)
    node3_c2 = Node(3, node2_c2)
    node4_c2 = Node(4, node3_c2)
    node5_c2 = Node(5, node4_c2) # Head is node5_c2 (5 -> 4 -> 3 -> 2 -> 1)
    node1_c2.successor = node5_c2 # Create cycle: 1 -> 5 (so 5 -> 4 -> 3 -> 2 -> 1 -> 5)

    if detect_cycle(node5_c2):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 3: 2-node list with cycle
    # Expected Output: Cycle detected!
    node1_c3 = Node(1)
    node2_c3 = Node(2, node1_c3) # Head is node2_c3 (2 -> 1)
    node1_c3.successor = node2_c3 # Create cycle: 1 -> 2 (so 2 -> 1 -> 2)

    if detect_cycle(node2_c3):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 4: 2-node list with no cycle
    # Expected Output: Cycle not detected!
    node6_c4 = Node(6)
    node7_c4 = Node(7, node6_c4)

    if detect_cycle(node7_c4):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 5: 1-node list
    # Expected Output: Cycle not detected!
    node_c5 = Node(0)
    if detect_cycle(node_c5):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()

    # Case 6: 5 nodes in total. the last 2 nodes form a cycle. input the first node
    # Expected Output: Cycle detected!
    node1_c6 = Node(1)
    node2_c6 = Node(2, node1_c6)
    node3_c6 = Node(3, node2_c6)
    node4_c6 = Node(4, node3_c6)
    node5_c6 = Node(5, node4_c6) # Head is node5_c6 (5 -> 4 -> 3 -> 2 -> 1)
    node1_c6.successor = node2_c6 # Create cycle: 1 -> 2 (so 5 -> 4 -> 3 -> 2 -> 1 -> 2)

    if detect_cycle(node5_c6):
        print("Cycle detected!", end=" ")
    else:
        print("Cycle not detected!", end=" ")
    print()


if __name__ == "__main__":
    main()