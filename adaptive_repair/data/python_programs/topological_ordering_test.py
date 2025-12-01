class Node:
    def __init__(self, value):
        self.value = value
        self.outgoing_nodes = []
        self.incoming_nodes = []

    def add_outgoing_edge(self, target_node):
        """
        Adds a directed edge from this node to the target_node,
        ensuring consistency between outgoing_nodes and incoming_nodes lists.
        """
        if target_node not in self.outgoing_nodes:
            self.outgoing_nodes.append(target_node)
        if self not in target_node.incoming_nodes:
            target_node.incoming_nodes.append(self)

    def __repr__(self):
        return f"Node({self.value})"

    def __eq__(self, other):
        # Nodes are considered equal if they are Node instances and have the same value.
        # This is crucial for 'not in' checks and dictionary keys.
        return isinstance(other, Node) and self.value == other.value

    def __hash__(self):
        # Hash based on value for consistent behavior with __eq__.
        return hash(self.value)

# Placeholder for topological_ordering, as it was imported from a separate file.
# This implementation uses Kahn's algorithm to produce a valid topological sort.
def topological_ordering(nodes):
    """
    Performs a topological sort on the given graph nodes using Kahn's algorithm.
    Raises an exception if a cycle is detected.
    """
    in_degree = {node: 0 for node in nodes}
    for node in nodes:
        for outgoing in node.outgoing_nodes:
            # Ensure the outgoing node is also in the initial 'nodes' list
            # to prevent KeyError if the graph is not fully represented in 'nodes'.
            if outgoing in in_degree:
                in_degree[outgoing] += 1
            else:
                # Handle cases where an outgoing node might not be in the initial 'nodes' list
                # For this problem, we assume all relevant nodes are passed.
                pass 

    queue = [node for node in nodes if in_degree[node] == 0]
    result = []

    while queue:
        current_node = queue.pop(0)  # Use pop(0) for FIFO queue behavior
        result.append(current_node)

        for neighbor in current_node.outgoing_nodes:
            if neighbor in in_degree: # Ensure neighbor is a tracked node
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    if len(result) != len(nodes):
        raise Exception("Graph has a cycle, topological ordering not possible.")

    return result


"""
Driver to test topological ordering
"""

# The global add_edge function has been removed.
# Its logic is now encapsulated within the Node.add_outgoing_edge method.

def main():
    # Case 1: Wikipedia graph
    # Output: 5 7 3 11 8 10 2 9
    
    five = Node(5)
    seven = Node(7)
    three = Node(3)
    eleven = Node(11)
    eight = Node(8)
    two = Node(2)
    nine = Node(9)
    ten = Node(10)

    # Using Node.add_outgoing_edge to ensure consistency for every edge.
    five.add_outgoing_edge(eleven)
    seven.add_outgoing_edge(eleven)
    seven.add_outgoing_edge(eight)
    three.add_outgoing_edge(eight)
    three.add_outgoing_edge(ten)
    eleven.add_outgoing_edge(two)
    eleven.add_outgoing_edge(nine)
    eleven.add_outgoing_edge(ten)
    eight.add_outgoing_edge(nine)

    try:
        all_nodes_case1 = [five, seven, three, eleven, eight, two, nine, ten]
        [print(x.value, end=" ") for x in topological_ordering(all_nodes_case1)]
    except Exception as e:
        print(e)
    print()


    # Case 2: GeekforGeeks example
    # Output: 4 5 0 2 3 1

    five = Node(5)
    zero = Node(0)
    four = Node(4)
    one = Node(1)
    two = Node(2)
    three = Node(3)

    # Using Node.add_outgoing_edge to ensure consistency for every edge.
    five.add_outgoing_edge(two)
    five.add_outgoing_edge(zero)
    four.add_outgoing_edge(zero)
    four.add_outgoing_edge(one)
    two.add_outgoing_edge(three)
    three.add_outgoing_edge(one)

    try:
        all_nodes_case2 = [zero, one, two, three, four, five]
        [print(x.value, end=" ") for x in topological_ordering(all_nodes_case2)]
    except Exception as e:
        print(e)
    print()
    

    # Case 3: Cooking with InteractivePython
    # Output: (No specific output provided, but should run without error)

    milk = Node("3/4 cup milk")
    egg = Node("1 egg")
    oil = Node("1 Tbl oil")
    mix = Node("1 cup mix")
    syrup = Node("heat syrup")
    griddle = Node("heat griddle")
    pour = Node("pour 1/4 cup")
    turn = Node("turn when bubbly")
    eat = Node("eat")

    # Using Node.add_outgoing_edge to ensure consistency for every edge.
    milk.add_outgoing_edge(mix)
    egg.add_outgoing_edge(mix)
    oil.add_outgoing_edge(mix)
    mix.add_outgoing_edge(syrup)
    mix.add_outgoing_edge(pour)
    griddle.add_outgoing_edge(pour)
    pour.add_outgoing_edge(turn)
    turn.add_outgoing_edge(eat)
    syrup.add_outgoing_edge(eat)

    try:
        all_nodes_case3 = [milk, egg, oil, mix, syrup, griddle, pour, turn, eat]
        [print(x.value, end=" ") for x in topological_ordering(all_nodes_case3)]
    except Exception as e:
        print(e)
    print()


if __name__ == "__main__":
    main()