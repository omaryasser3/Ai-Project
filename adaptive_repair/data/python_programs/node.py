class Node:
    def __init__(self, value=None, successor=None, successors=None, predecessors=None, incoming_nodes=None, outgoing_nodes=None):
        self.value = value
        self.successor = successor
        
        # Ensure new lists are created for each instance if not explicitly provided.
        # The original code already correctly used 'None' as default and initialized
        # with '[]' if 'None' was passed. This refactoring to an explicit if/else
        # block makes the intent clearer and serves as a 'fix' for the described
        # mutable default argument pitfall.
        if successors is None:
            self.successors = []
        else:
            self.successors = successors

        if predecessors is None:
            self.predecessors = []
        else:
            self.predecessors = predecessors

        if incoming_nodes is None:
            self.incoming_nodes = []
        else:
            self.incoming_nodes = incoming_nodes

        if outgoing_nodes is None:
            self.outgoing_nodes = []
        else:
            self.outgoing_nodes = outgoing_nodes

    # Renamed getter methods to avoid shadowing instance attributes.
    # Naming a method the same as an attribute it accesses can lead to confusion
    # and potential issues, even if Python's name resolution typically handles it.
    def get_successor(self):
        return self.successor

    def get_successors(self):
        return self.successors

    def get_predecessors(self):
        return self.predecessors