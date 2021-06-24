#!/usr/bin/python3
from node import Node
import math
from pairing_heap_interface import PairingHeapInterface


class SmoothHeapL(PairingHeapInterface):
    """lazy implementation of smooth heap without buffer"""
    forest = []  # list storing roots of all top-level trees
    minNode = None
    updates = 0

    def __init__(self, root=None):
        self.forest = []
        if root != None:
            root.parent = None
            self.updates += 1
            root.nextSibling = root
            self.updates += 1
            self.minNode = root
            self.updates += 1
            self.forest += [root]

    def make_heap(self):
        # this is equivalent to init
        pass

    def find_min(self):
        return self.minNode

    def listPreOrderHelper(self, root):
        res = []
        if root.rightChild == None:
            return [root.key]
        else:
            current = root.rightChild
            res += [root.key, self.listPreOrderHelper(current)]
            while current.nextSibling != root.rightChild:
                current = current.nextSibling
                res += [self.listPreOrderHelper(current)]
            return [res]

    def listPreOrder(self):
        res = []
        buf = []
        for item in self.forest:
            res += self.listPreOrderHelper(item)
        print(res)

    def stable_link_left(self, left, right):
        """left node becomes parent of right node"""
        if left.rightChild != None:
            right.nextSibling = left.rightChild.nextSibling
            self.updates += 1
            left.rightChild.nextSibling = right
            self.updates += 1
        else:
            right.nextSibling = right
            self.updates += 1
        left.rightChild = right
        self.updates += 1
        right.parent = left
        self.updates += 1

    def stable_link_right(self, left, right):
        """right node becomes parent of left node"""
        if right.rightChild is None:
            right.rightChild = left
            self.updates += 1
            left.nextSibling = left
            self.updates += 1
        else:
            left.nextSibling = right.rightChild.nextSibling
            self.updates += 1
            right.rightChild.nextSibling = left
            self.updates += 1
        left.parent = right
        self.updates += 1

    def insert(self, node):
        """concatenates node to list of trees in pool"""
        if node is None:
            return (0, 0)  # no comparisons, no links
        node.nextSibling = node
        self.updates += 1
        node.parent = None
        self.updates += 1
        self.forest += [node]
        return (0, 0)  # 1 comparison, no links

    def merge(self, heap2):
        """concatenates root lists of heaps"""
        if heap2 is None:
            return (0, 0)
        compCount = 0
        linkCount = 0
        if len(self.forest) > len(heap2.forest):
            # first heap larger than second
            self.forest += heap2.forest
        else:
            self.forest = heap2.forest + self.forest
        return (compCount, linkCount)

    def delete_min(self):
        """consolidates into single tree; extracts min node,
        placing its orphaned children in root list.
        Returns min node, number comparisons, number links"""
        if len(self.forest) == 0:
            return (None, 0, 0)
        (cc, lc) = self.treapify()
        assert len(self.forest) == 1
        minKeyNode = self.minNode
        minNodeChildren = []

        if self.minNode.rightChild is not None:
            minNodeChildren += [self.minNode.rightChild]
            self.minNode.rightChild.parent = None
            self.updates += 1
            current = self.minNode.rightChild.nextSibling
            self.minNode.rightChild.nextSibling = self.minNode.rightChild
            self.updates += 1

            while current != self.minNode.rightChild:
                minNodeChildren += [current]
                tempNode = current
                current = current.nextSibling
                tempNode.nextSibling = tempNode
                self.updates += 1
                tempNode.parent = None
                self.updates += 1
        self.forest = minNodeChildren
        return (minKeyNode, cc, lc)

    def treapify(self):
        """links roots in pool (forest) into treap and returns number of links/comparisons
        this uses the pseudocode of delete-min from https://arxiv.org/abs/1802.05471
        returns number comparisons, number link operations performed"""
        linkCount = 0  # counts only number of links
        compCount = 0  # counts only number of comparisons
        fs = len(self.forest)
        if len(self.forest) == 0:  # pool is empty
            self.minNode = None
            self.updates += 1
            return (compCount, linkCount)

        elif len(self.forest) == 1:
            self.minNode = self.forest[0]
            self.updates += 1
            return (compCount, linkCount)

        else:
            i = 0
            curr_forest = self.forest
            while i < len(curr_forest) - 1:
                compCount += 1  # first if-else comparison
                if curr_forest[i].key < curr_forest[i + 1].key:
                    i = i + 1
                else:
                    skip = False
                    while i > 0:
                        compCount += 1
                        linkCount += 1
                        if curr_forest[i - 1].key > curr_forest[i + 1].key:
                            # stable-link predecessor as parent of current node
                            self.stable_link_left(curr_forest[i - 1], curr_forest[i])
                            # remove node at index i from top-list
                            curr_forest = curr_forest[:i] + curr_forest[i + 1:]
                            i = i - 1
                        else:
                            # stable-link successor as parent of current node
                            self.stable_link_right(curr_forest[i], curr_forest[i + 1])
                            # remove node at index i from top-list
                            curr_forest = curr_forest[:i] + curr_forest[i + 1:]
                            # i=i+1
                            skip = True
                            break
                    if not skip:  # i==0
                        # stable-link current as leftmost child of successor
                        self.stable_link_right(curr_forest[i], curr_forest[i + 1])
                        # remove node from top-list
                        curr_forest = curr_forest[i + 1:]
                        linkCount += 1

            while i > 0:
                # stable-link predecessor as parent of current node
                self.stable_link_left(curr_forest[i - 1], curr_forest[i])
                curr_forest = curr_forest[:i]
                linkCount += 1
                i = i - 1
            self.forest = curr_forest
            assert len(self.forest) == 1
            self.minNode = self.forest[0]
            self.updates += 1
        assert (fs - 1 == linkCount)
        return (compCount, linkCount)


    def decrease_key(self, node, diff):
        """removes node with subtree from current position;
        decreases key; places node in root list."""
        assert node is not None
        node.key = node.key - diff
        self.updates += 1
        # concatenates node to list of trees in pool

        if node.parent is None:  # node is a root and has children
            if node in self.forest:
                pass  # leave in-place
            else:
                self.listPreOrder()
                raise Exception("node with key {} is not in heap".format(node.key))
        else:  # node is not a root

            if node.nextSibling == node:  # node has no siblings
                node.parent.rightChild = None
                self.updates += 1

            else:  # node has siblings
                current = node.nextSibling
                while current.nextSibling != node:  # find predecessor of node
                    current = current.nextSibling
                current.nextSibling = node.nextSibling
                self.updates += 1
                if node.parent.rightChild == node:
                    node.parent.rightChild = current
                    self.updates += 1

            node.parent = None
            self.updates += 1
            node.nextSibling = node
            self.updates += 1
            self.forest += [node]
        return (0, 0)

    def pointer_updates(self):
        return self.updates