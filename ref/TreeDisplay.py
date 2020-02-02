"""
Python class definition for drawing trees using SimpleGUI
"""

import simplegui

NODE_HEIGHT = 100
NODE_WIDTH = 100

class TreeDisplay:
    """
    Class to display a given tree on the canvas
    """

    def __init__(self, tree):
        """
        Create GUI
        """
        self._tree = tree
        self._canvas_width, self._canvas_height = self.get_box_size(tree)
        self._frame = simplegui.create_frame("Draw a tree", self._canvas_width, self._canvas_height)
        self._frame.set_canvas_background("White")
        self._frame.set_draw_handler(self.draw)
        self._frame.start()
        
        
    def get_box_size(self, tree):
        """
        Recursive function to compute height and width
        of the bounding box for a tree
        """
        current_subtree_widths = 0
        tree_height = 0
        for child in tree.children():
            child_width, child_height = self.get_box_size(child)
            current_subtree_widths += child_width
            tree_height = max(tree_height, child_height)                            
        subtree_width = max(NODE_WIDTH, current_subtree_widths)
        tree_height = NODE_HEIGHT + tree_height
        return subtree_width, tree_height
        

    def draw_tree(self, canvas, tree, pos):
        """ 
        Recursively draw a tree on the canvas
        pos is the position of the upper left corner of the bounding box
        """

        # compute horizontal position for left boundary of each subtree
        horiz_boundaries = [pos[0]]
        for child in tree.children():
            child_width, dummy_child_height = self.get_box_size(child)
            horiz_boundaries.append(horiz_boundaries[-1] + child_width)
            
        # draw lines from root to children, must draw first                    
        width = max(NODE_WIDTH, horiz_boundaries[-1] - horiz_boundaries[0])
        root_center = [pos[0] + width / 2, pos[1] + NODE_HEIGHT / 2]
        for idx in range(len(horiz_boundaries) - 1):
            child_center = [(horiz_boundaries[idx] + horiz_boundaries[idx + 1]) / 2, 
                             pos[1] + 3 * NODE_HEIGHT / 2]
            canvas.draw_line(root_center, child_center, 3, "Black")
                       
        # draw root
        canvas.draw_circle(root_center, NODE_HEIGHT / 4, 2, "Black", "LightGreen")
        text_pos = [root_center[0] - NODE_HEIGHT / 12, root_center[1] + NODE_HEIGHT / 12]
        canvas.draw_text(tree.get_value(), text_pos, NODE_HEIGHT / 4, "Black") 

        #draw children
        for child, bndry in zip(tree.children(), horiz_boundaries):
            self.draw_tree(canvas, child, [bndry, pos[1] + NODE_HEIGHT])
        
    def draw(self, canvas):
        """
        Draw handler for tree drawing
        """
        self.draw_tree(canvas, self._tree, [0, 0])
    


