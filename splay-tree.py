from node import Node

class SplayTree:
    def __init__(self):
        self.root = None

    # rotate left at node x
    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        x.min = min(x.key, x.left.min, x.right.min)
        y.min = min(y.key, y.left.min, y.right.min)

    # rotate left at node y
    def right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        x.min = min(x.key, x.left.min, x.right.min)
        y.min = min(y.key, y.left.min, y.right.min)

    # move x to the root of the tree
    def splay(self, x):
        if x.parent is None:
            return
        # ZIG parent(x) is root
        if x.parent.parent is None:
            if x == x.parent.left:
                self.right_rotate(x.parent)
            else:
                self.left_rotate(x.parent)

        # ZIG-ZIG x, parent(x) are both left/right children
        elif x == x.parent.left and x.parent == x.parent.parent.left:
            self.right_rotate(x.parent.parent)
            self.right_rotate(x.parent)
        elif x == x.parent.right and x.parent == x.parent.parent.right:
            self.left_rotate(x.parent.parent)
            self.left_rotate(x.parent)

        # ZIG-ZAG x is left child, parent(x) is right or vice-versa
        elif x == x.parent.right and x.parent == x.parent.parent.left:
            self.left_rotate(x.parent)
            self.right_rotate(x.parent)

        elif x == x.parent.left and x.parent == x.parent.parent.right:
            self.right_rotate(x.parent)
            self.left_rotate(x.parent)

        self.splay(self, x)

    def left(self, x):
        if x.left is None:
            return x
        return self.left(x.left)

    def right(self, x):
        if x.right is None:
            return x
        return self.right(x.right)

    # new leftmost node and splay to the root
    def insert(self, x):
        leftmost = self.left(self.root)
        leftmost.left = x
        x.parent = leftmost
        self.splay(x)

    def find_min_node(self, x):
        if x.key == self.root.min:
            return x
        # elif x.left is None and x.right is None:
        #     return x
        elif x.left is None:
            return self.find_min_node(x.right)
        elif x.right is None:
            return self.find_min_node(x.left)
        else:
            return min(self.find_min_node(x.left), self.find_min_node(x.right))

    def find_min(self):
        return self.find_min_node(self.root)

    def delete(self, x):
        if x.left is not None and x.right is not None:
            # rightmost in left subtree
            predecessor = self.right(x.left)
            x.key, predecessor.key = predecessor.key, x.key
        parent = x.parent
        # leaf, delete it
        if x.left is not None and x.left.left is None and x.left.right is None:
            x.left.parent.left = None
        elif x.right is not None and x.right.left is None and x.right.right is None:
            x.right.parent.right = None
        # one child
        elif x.left is not None:
            if x == x.parent.left:
                x.parent.left = x.left
            else:
                x.parent.right = x.left
        else:
            if x == x.parent.left:
                x.parent.left = x.right
            else:
                x.parent.right = x.right
        self.splay(parent)

    def delete_min(self):
        return self.find_min()