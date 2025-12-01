from collections import deque

# Define Node class directly as it's part of the architectural fix
class Node:
    def __init__(self, value):
        self.value = value
        self.outgoing_nodes = []
        # incoming_nodes is removed to enforce a single source of truth for edges.
        # In-degrees will be computed dynamically by the topological_ordering algorithm.

    def add_outgoing_edge(self, destination: 'Node'):
        """Adds a directed edge from this node to the destination, ensuring no duplicates."""
        if destination not in self.outgoing_nodes:
            self.outgoing_nodes.append(destination)

    def __repr__(self):
        return f"Node({self.value})"

# Define topological_ordering directly as it's part of the architectural fix
def topological_ordering(nodes: list[Node]) -> list[Node]:
    """
    Performs topological sorting using Kahn's algorithm.
    It dynamically computes in-degrees from the 'outgoing_nodes' list,
    as 'incoming_nodes' are no longer explicitly stored on Node objects.
    """
    in_degree = {node: 0 for node in nodes}
    
    # Compute in-degrees for all nodes by iterating through outgoing edges
    for node in nodes:
        for neighbor in node.outgoing_nodes:
            # Ensure the neighbor is part of the graph being processed
            if neighbor in in_degree:
                in_degree[neighbor] += 1
            else:
                # This case indicates an edge to a node not in the provided 'nodes' list.
                # For a well-formed graph, all nodes should be in 'nodes'.
                # Depending on requirements, this could raise an error or ignore.
                pass 

    # Initialize queue with all nodes having an in-degree of 0
    queue = deque([node for node in nodes if in_degree[node] == 0])
    
    topological_order = []
    
    while queue:
        u = queue.popleft() # Efficient dequeue from the left
        topological_order.append(u)
        
        # For each neighbor of the dequeued node, decrement its in-degree
        for v in u.outgoing_nodes:
            in_degree[v] -= 1
            # If a neighbor's in-degree becomes 0, add it to the queue
            if in_degree[v] == 0:
                queue.append(v)
                
    # Check for cycles: if the number of nodes in the topological order
    # is less than the total number of nodes, a cycle exists.
    if len(topological_order) != len(nodes):
        raise Exception("Graph has a cycle, topological ordering not possible.")
        
    return topological_order


"""
Driver to test topological ordering
"""
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

    # Removed redundant list clearing. Node.__init__ already initializes lists,
    # and incoming_nodes is no longer a direct attribute.

    # Use the add_outgoing_edge method on Node objects
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
        [print(x.value, end=" ") for x in topological_ordering([five, seven, three, eleven, eight, two, nine, ten])]
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

    # Removed redundant list clearing

    five.add_outgoing_edge(two)
    five.add_outgoing_edge(zero)
    four.add_outgoing_edge(zero)
    four.add_outgoing_edge(one)
    two.add_outgoing_edge(three)
    three.add_outgoing_edge(one)

    try:
        [print(x.value, end=" ") for x in topological_ordering([zero, one, two, three, four, five])]
    except Exception as e:
        print(e)
    print()
    

    # Case 3: Cooking with InteractivePython
    # Output: (No specific output given, but should be a valid topological order)

    milk = Node("3/4 cup milk")
    egg = Node("1 egg")
    oil = Node("1 Tbl oil")
    mix = Node("1 cup mix")
    syrup = Node("heat syrup")
    griddle = Node("heat griddle")
    pour = Node("pour 1/4 cup")
    turn = Node("turn when bubbly")
    eat = Node("eat")

    # Removed redundant list clearing

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
        [print(x.value, end=" ") for x in topological_ordering([milk, egg, oil, mix, syrup, griddle, pour, turn, eat])]
    except Exception as e:
        print(e)
    print()


if __name__ == "__main__":
    main()