from node import Node
from pairing_heap_interface import PairingHeapInterface

class SplayTree(PairingHeapInterface):
    updates = 0
    def __init__(self):
        self.root = None

    # rotate left at node x
    def left_rotate(self, x):
        y = x.rightChild
        x.rightChild = y.leftChild
        self.updates += 1
        if y.leftChild is not None:
            y.leftChild.parent = x
            self.updates += 1
        y.parent = x.parent
        self.updates += 1
        if x.parent is None:
            self.root = y
        elif x == x.parent.leftChild:
            x.parent.leftChild = y
        else:
            x.parent.rightChild = y
        self.updates += 1
        y.leftChild = x
        self.updates += 1
        x.parent = y
        self.updates += 1

        x.min = x.key
        if x.leftChild is not None:
            x.min = min(x.min, x.leftChild.min)
        if x.rightChild is not None:
            x.min = min(x.min, x.rightChild.min)
        self.updates += 1

        y.min = y.key
        if y.leftChild is not None:
            y.min = min(y.min, y.leftChild.min)
        if y.rightChild is not None:
            y.min = min(y.min, y.rightChild.min)
        self.updates += 1

        # x.min = min(x.key, x.leftChild.min, x.rightChild.min)
        # y.min = min(y.key, y.leftChild.min, y.rightChild.min)

    # rotate left at node y
    def right_rotate(self, x):
        y = x.leftChild
        x.leftChild = y.rightChild
        if y.rightChild is not None:
            y.rightChild.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.rightChild:
            x.parent.rightChild = y
        else:
            x.parent.leftChild = y
        y.rightChild = x
        x.parent = y

        x.min = x.key
        if x.leftChild is not None:
            x.min = min(x.min, x.leftChild.min)
        if x.rightChild is not None:
            x.min = min(x.min, x.rightChild.min)

        y.min = y.key
        if y.leftChild is not None:
            y.min = min(y.min, y.leftChild.min)
        if y.rightChild is not None:
            y.min = min(y.min, y.rightChild.min)

        #x.min = min(x.key, x.leftChild.min, x.rightChild.min)
        #y.min = min(y.key, y.left.min, y.rightChild.min)

    # move x to the root of the tree
    def splay(self, x):
        if x.parent is None:
            return
        # ZIG parent(x) is root
        if x.parent.parent is None:
            if x == x.parent.leftChild:
                self.right_rotate(x.parent)
            else:
                self.left_rotate(x.parent)

        # ZIG-ZIG x, parent(x) are both left/right children
        elif x == x.parent.leftChild and x.parent == x.parent.parent.leftChild:
            self.right_rotate(x.parent.parent)
            self.right_rotate(x.parent)
        elif x == x.parent.rightChild and x.parent == x.parent.parent.rightChild:
            self.left_rotate(x.parent.parent)
            self.left_rotate(x.parent)

        # ZIG-ZAG x is left child, parent(x) is right or vice-versa
        elif x == x.parent.rightChild and x.parent == x.parent.parent.leftChild:
            self.left_rotate(x.parent)
            self.right_rotate(x.parent)

        elif x == x.parent.leftChild and x.parent == x.parent.parent.rightChild:
            self.right_rotate(x.parent)
            self.left_rotate(x.parent)

        self.splay(x)

    def left(self, x):
        if x is None:
            return x
        if x.leftChild is None:
            return x
        return self.left(x.leftChild)

    def right(self, x):
        if x is None:
            return x
        if x.rightChild is None:
            return x
        return self.right(x.rightChild)

    # new leftmost node and splay to the root
    def insert(self, x):
        leftmost = self.left(self.root)
        if leftmost is None:
            self.root = x
            self.updates += 1
            return
        leftmost.leftChild = x
        self.updates += 1
        x.parent = leftmost
        self.updates += 1
        self.splay(x)

    def find_min_node(self, x):
        if x.key == self.root.min:
            return x
        # elif x.left is None and x.right is None:
        #     return x
        elif x.leftChild is None:
            return self.find_min_node(x.rightChild)
        elif x.rightChild is None:
            return self.find_min_node(x.leftChild)
        else:
            return min(self.find_min_node(x.leftChild), self.find_min_node(x.rightChild))

    def find_min(self):
        return self.find_min_node(self.root)

    def delete(self, x):
        if x.leftChild is not None and x.rightChild is not None:
            # rightmost in left subtree
            predecessor = self.right(x.leftChild)
            x.key, predecessor.key = predecessor.key, x.key
        parent = x.parent
        # leaf, delete it
        if x.leftChild is not None and x.leftChild.leftChild is None and x.leftChild.rightChild is None:
            x.leftChild.parent.leftChild = None
        elif x.rightChild is not None and x.rightChild.leftChild is None and x.rightChild.rightChild is None:
            x.rightChild.parent.rightChild = None
        # one child
        elif x.leftChild is not None:
            if x == x.parent.leftChild:
                x.parent.leftChild = x.leftChild
            else:
                x.parent.rightChild = x.leftChild
        else:
            if x == x.parent.leftChild:
                x.parent.leftChild = x.rightChild
            else:
                x.parent.rightChild = x.rightChild
        self.updates += 1
        self.splay(parent)

    def delete_min(self):
        return self.delete(self.find_min())

    def in_order(self, node):
        if node is not None:
            self.in_order(node.leftChild)
            print(node.key)
            self.in_order(node.rightChild)

    def pointer_updates(self):
        return self.updates

if __name__ == "__main__":
    tree = SplayTree()
    tree.insert(Node(3))
    tree.insert(Node(4))
    tree.insert(Node(5))
    tree.in_order(tree.root)
    print(tree.find_min().key)
    tree.delete_min()
    print(tree.find_min().key)