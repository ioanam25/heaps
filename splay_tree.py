import random

from node import Node
from pairing_heap_interface import PairingHeapInterface
import numpy as np
import sys
sys.setrecursionlimit(100000)

class SplayTree(PairingHeapInterface):
    updates = 0
    links = 0
    comps = 0

    def __init__(self):
        self.root = None


    # rotate left at node x
    def left_rotate(self, x):
        # print("rotate left")
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

        self.comps += 4

    # rotate left at node y
    def right_rotate(self, x):
        # print("rotate right")
        y = x.leftChild
        x.leftChild = y.rightChild
        self.updates += 1
        if y.rightChild is not None:
            y.rightChild.parent = x
            self.updates += 1
        y.parent = x.parent
        self.updates += 1
        if x.parent is None:
            self.root = y
        elif x == x.parent.rightChild:
            x.parent.rightChild = y
        else:
            x.parent.leftChild = y
        self.updates += 1
        y.rightChild = x
        self.updates += 1
        x.parent = y
        self.updates += 1

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

        self.comps += 1

    def splay(self, x):
        while x.parent != None:
            if x.parent.parent == None:
                if x == x.parent.leftChild:
                    # zig rotation
                    self.right_rotate(x.parent)
                else:
                    # zag rotation
                    self.left_rotate(x.parent)
            elif x == x.parent.leftChild and x.parent == x.parent.parent.leftChild:
                # zig-zig rotation
                self.right_rotate(x.parent.parent)
                self.right_rotate(x.parent)
            elif x == x.parent.rightChild and x.parent == x.parent.parent.rightChild:
                # zag-zag rotation
                self.left_rotate(x.parent.parent)
                self.left_rotate(x.parent)
            elif x == x.parent.rightChild and x.parent == x.parent.parent.leftChild:
                # zig-zag rotation
                self.left_rotate(x.parent)
                self.right_rotate(x.parent)
            elif x == x.parent.leftChild and x.parent == x.parent.parent.rightChild:
                # zag-zig rotation
                self.right_rotate(x.parent)
                self.left_rotate(x.parent)
            else:
                print("broke")
                return None

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
        x.leftChild = None
        x.rightChild = None
        x.min = x.key
        self.updates += 3
        self.links += 1
        self.splay(x)

    def find_min_node(self, x):
        x = self.root
        assert self.root is not None
        while x.key != self.root.min:
            if x.leftChild is None and x.rightChild is None:
                print("buugggg")
            elif x.leftChild is None:
                x = x.rightChild
            elif x.rightChild is None:
                x = x.leftChild
            else:
                if x.leftChild.min == self.root.min:
                    x = x.leftChild
                elif x.rightChild.min == self.root.min:
                    x = x.rightChild
                else:
                    print("bug3000")
            self.updates += 1

        return x

    def listInorderTree(self, root):
        if root is None:
            return []
        else:
            return self.listInorderTree(root.leftChild) + [root.key] + self.listInorderTree(root.nextSibling)

    def find_min(self):
        print(self.listInorderTree(self.root))
        x = self.find_min_node(self.root)
        if x.key != self.root.min:
            print("nope")
        print(x.key)
        return x

    def delete(self, x):
        if x.leftChild is not None and x.rightChild is not None:
            # rightmost in left subtree
            predecessor = self.right(x.leftChild)
            x.key, predecessor.key = predecessor.key, x.key
            x = predecessor
            self.updates += 1

        if x.parent is not None:
            parent = x.parent
        else:
            parent = None

        # leaf, delete it
        if x.leftChild is None and x.rightChild is None:
            if x.parent is not None:
                if x.parent.leftChild == x:
                    x.parent.leftChild = None
                else:
                    x.parent.rightChild = None
                self.updates += 1
        # one child
        elif x.leftChild is not None:
            if x.parent is not None:
                if  x == x.parent.leftChild: # TODO check
                    x.parent.leftChild = x.leftChild
                    x.leftChild.parent = x.parent
                else:
                    x.parent.rightChild = x.leftChild
                    x.leftChild.parent = x.parent
            else:
                self.root = x.leftChild
                x.leftChild.parent = None
        elif x.rightChild is not None:
            if x.parent is not None:
                if  x == x.parent.leftChild:
                    x.parent.leftChild = x.rightChild
                    x.rightChild.parent = x.parent
                else:
                    x.parent.rightChild = x.rightChild
                    x.rightChild.parent = x.parent
            else:
                self.root = x.rightChild
                x.rightChild.parent = None
        else:
            print("NO")
        self.updates += 2

        if parent is None:
            if self.root.leftChild is not None:
                self.root.min = min(self.root.min, self.root.leftChild.min)
            if self.root.rightChild is not None:
                self.root.min = min(self.root.min, self.root.rightChild.min)
            self.updates += 1
        else:
            parent.min = parent.key
            if parent.leftChild is not None:
                parent.min = min(parent.min, parent.leftChild.min)
            if parent.rightChild is not None:
                parent.min = min(parent.min, parent.rightChild.min)
            self.updates += 2
            if self.root is None:
                print("CRY before splay")
            self.splay(parent)
            if self.root is None:
                print("cry after splay")
        if self.root is None:
            print("cry")

        return x
        # note new min updates in rotations during splay

    def delete_min(self):
        return (self.delete(self.find_min()), self.comps, self.links)

    # def in_order(self, node):
    #     if node is not None:
    #         if node.leftChild is not None:
    #             self.in_order(node.leftChild)
    #         print(node.key)
    #         if node.rightChild is not None:
    #             self.in_order(node.rightChild)

    def pointer_updates(self):
        return self.updates

# if __name__ == "__main__":
#     tree = SplayTree()
#     #tree.insert(Node(3))
#     #tree.insert(Node(4))
#     tree.insert(Node(5))
#     tree.insert(Node(7))
#     #tree.insert(Node(8))
#     tree.insert(Node(1))
#     tree.insert(Node(10))
#     #tree.insert(Node(9))
#     tree.in_order(tree.root)
#     print(tree.find_min().key)
#     tree.delete_min()
#     print(tree.find_min().key)