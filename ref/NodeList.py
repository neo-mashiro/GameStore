"""
Recursive class definition for a non-empty list of nodes
"""


class NodeList:
    """
    Basic class definition for non-empty lists using recursion
    """
    
    def __init__(self, val):
        """
        Create a list with one node
        """
        self._value = val
        self._next = None
     
    
    def append(self, val):
        """
        Append a node to an existing list of nodes
        """
        if self._next == None:
            new_node = NodeList(val)
            self._next = new_node
        else:
            self._next.append(val)
            

    def __str__(self):
        """
        Build standard string representation for list
        """
        if self._next == None:
            return "[" + str(self._value) + "]"
        else:
            rest_str = str(self._next)
            rest_str = rest_str[1 :]
            return "[" + str(self._value) + ", " + rest_str
    
def run_example():
    """
    Create some examples
    """
    node_list = NodeList(2)
    node_list.append(3)
    node_list.append(4)
    print node_list
    
    sub_list = NodeList(5)
    sub_list.append(6)
    
    node_list.append(sub_list)
    print node_list
    
run_example()