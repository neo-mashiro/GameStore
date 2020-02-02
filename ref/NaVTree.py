"""
Python definition of navigable Tree class
"""

import poc_tree

class NavTree(poc_tree.Tree):
    """
    Recursive definition for navigable trees plus extra tree methods
    """
    
    def __init__(self, value, children, parent = None):
        """
        Create a tree whose root has specific value (a string)
        children is a list of references to the roots of the children.  
        parent (if specified) is a reference to the tree's parent node
        """
        
        poc_tree.Tree.__init__(self, value, children)
        self._parent = parent
        for child in self._children:
            child._parent = self          
    
    def set_parent(self, parent):
        """
        Update parent field
        """
        self._parent = parent
               
            
    def get_root(self):
        """
        Return the root of the tree
        """
        if self._parent is None:
            return self
        else:
            return self._parent.get_root()

    def depth(self):
        """
        Return the depth of the self with respect to the root of the tree
        """
        if self._parent is None:
            return 0
        else:
            return self._parent.depth() + 1
    
def run_examples():
    """
    Create some trees and apply various methods to these trees
    """
    tree_a = NavTree("a", [])
    tree_b = NavTree("b", [])
    tree_cab = NavTree("c", [tree_a, tree_b]) 
    tree_e = NavTree("e", [])
    tree_dcabe = NavTree("d", [tree_cab, tree_e])
    
    print "This is the main tree -", tree_dcabe
    print "This is tree that contains b -", tree_b.get_root()
    
    import poc_draw_tree
    poc_draw_tree.TreeDisplay(tree_dcabe)

    print "The node b has depth", tree_b.depth()
    print "The node e has depth", tree_e.depth()
             
run_examples()

# Expect output

#This is the main tree - [d, [c, [a], [b]], [e]]
#This is tree that contains b - [d, [c, [a], [b]], [e]]
#The node b has depth 2
#The node e has depth 1
