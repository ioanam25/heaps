#!/usr/bin/python3
from node import Node
import math
import sys
from pairing_heap_interface import PairingHeapInterface

sys.setrecursionlimit(100000)

class SmoothHeap(PairingHeapInterface):
    forest = []  # list storing roots of all top-level trees not in buffer
    buffer = []  # decrease buffer
    minNode = None
    size = 0
    updates = 0

    def __init__(self, root=None):
        self.forest = []
        self.buffer = []
        if root is not None:
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
        if root.rightChild is None:
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
        for elem in self.buffer:
            buf += self.listPreOrderHelper(elem)
        print("buffer: {}".format(buf))

    def stable_link_left(self, left, right):
        """left node becomes parent of right node"""
        if left.rightChild is not None:
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
        """concatenates node to list of roots in forest list"""
        if node is None:
            return (0, 0)  # no comparisons, no links
        node.nextSibling = node
        self.updates += 1
        node.parent = None
        self.updates += 1
        self.forest += [node]
        self.size += 1
        if self.minNode is None or node.key <= self.minNode.key:
            self.minNode = node
            self.updates += 1
        return (1, 0)  # 1 comparison, no links

    def merge(self, heap2):
        """cleans buffer of smaller heap, then concatenates forest lists
        returns number of comparisons and link operations"""
        if heap2 is None:
            return (0, 0)
        compCount = 0
        linkCount = 0
        if len(self.forest) + len(self.buffer) > len(heap2.forest) + len(heap2.buffer):
            # first heap larger than second
            (cc, lc) = heap2.clean_buffer()
            linkCount += lc
            compCount += cc + 1  # accounting for minNode comparison (at the end) as well
            self.forest += heap2.forest
        else:
            (cc, lc) = self.clean_buffer()
            linkCount += lc
            compCount += cc + 1  # accounting for minNode comparison (at the end) as well
            self.forest = heap2.forest + self.forest
            self.buffer = heap2.buffer
        self.size += heap2.size
        if (self.minNode.key >= heap2.minNode.key):
            self.minNode = heap2.minNode
            self.updates += 1
        return (compCount, linkCount)

    def delete_min(self):
        """consolidates and empties buffer, replaces minimum by its children in root list,
        then consolidates root list.
        Returns minNode, number of comparisons, number of link operations"""
        (compCount, linkCount) = self.clean_buffer()
        if self.minNode is None or len(self.forest) + len(self.buffer) == 0:  # this should be the same
            return (None, 0, 0)
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
        idx = self.forest.index(self.minNode)
        self.forest = self.forest[:idx] + minNodeChildren + self.forest[idx + 1:]  # replace minNode with its children
        self.size -= 1
        (cc, lc) = self.treapify()
        return (minKeyNode, compCount + cc, linkCount + lc)

    def treapify(self):
        """links roots in pool (forest) into treap
        (this uses the pseudocode of delete-min from https://arxiv.org/abs/1802.05471)
        returns number of links/comparisons
        """
        linkCount = 0  # counts only number of links
        compCount = 0  # counts only number of comparisons
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
        return (compCount, linkCount)

    def mergesort(self, llist):
        # standard mergesort, implemented to count comparisons properly
        if len(llist) < 2:
            return 0, llist
        split_idx = int(math.floor(len(llist) / 2))
        compsleft, lleft = self.mergesort(llist[:split_idx])
        compsright, lright = self.mergesort(llist[split_idx:])
        l = 0
        r = 0
        comps = compsleft + compsright
        sorted = []
        while l + r < len(llist):
            if r == len(lright) or (l < len(lleft) and lleft[l].key <= lright[r].key):
                sorted += [lleft[l]]
                l += 1
            else:
                sorted += [lright[r]]
                r += 1
            comps += 1
        return comps, sorted

    def clean_buffer(self):
        if len(self.buffer) == 0:  # buffer is empty
            return (0, 0)
        comps, self.buffer = self.mergesort(self.buffer)
        self.buffer.reverse()
        n = len(self.buffer)

        while len(self.buffer) > 1:
            self.stable_link_right(self.buffer[0], self.buffer[1])
            self.buffer = self.buffer[1:]

        treapified = self.buffer[0]
        self.buffer = []
        (compCount, linkCount) = self.merge(SmoothHeap(treapified))

        return (compCount + comps, linkCount + n - 1)  # (n-1)links while consolidating

    def decrease_key(self, node, diff):
        """cut out node from current location, leaving leftmost child;
        decrease key; place node with remaining subtree in buffer.
        Returns number of comparisons, links"""
        assert node is not None
        linkCount = 0
        compCount = 0
        node.key = node.key - diff
        self.updates += 1

        if node.parent is None and node.rightChild is None:  # node is root and has no children
            # could just leave this in place alternatively
            if node in self.forest:
                idx = self.forest.index(node)
                self.forest = self.forest[:idx] + self.forest[idx + 1:]
                self.buffer += [node]
            elif node in self.buffer:
                pass
            else:
                self.listPreOrder()
                raise Exception("node with key {} is not in heap".format(node.key))

        elif node.parent is None:  # node is a root and has children
            leftChild = node.rightChild.nextSibling
            if leftChild.nextSibling != leftChild:
                node.rightChild.nextSibling = leftChild.nextSibling  # cut out leftmost child
                self.updates += 1
            else:
                node.rightChild = None
                self.updates += 1
            leftChild.nextSibling = leftChild
            self.updates += 1
            leftChild.parent = None
            self.updates += 1
            if node in self.forest:
                idx = self.forest.index(node)  # remove node from pool and replace with leftChild
                self.forest = self.forest[:idx] + [leftChild] + self.forest[idx + 1:]
                self.buffer += [node]
            elif node in self.buffer:
                pass
            else:
                self.listPreOrder()
                raise Exception("node with key {} is not in heap".format(node.key))
        else:  # node is not a root
            leftChild = None
            if node.rightChild is not None:
                leftChild = node.rightChild.nextSibling
                leftChild.parent = node.parent
                self.updates += 1
            current = node.parent.rightChild

            if node.nextSibling == node and leftChild is not None:  # node not a leaf and has no siblings
                if leftChild.nextSibling != leftChild:
                    node.rightChild.nextSibling = leftChild.nextSibling  # cut out leftmost child
                    self.updates += 1
                else:
                    node.rightChild = None
                    self.updates += 1
                leftChild.nextSibling = leftChild
                self.updates += 1
                node.parent.rightChild = leftChild
                self.updates += 1

            elif leftChild is not None:  # node is not a leaf and has siblings
                if leftChild.nextSibling != leftChild:
                    node.rightChild.nextSibling = leftChild.nextSibling  # cut out leftmost child
                    self.updates += 1
                else:
                    node.rightChild = None
                    self.updates += 1
                while current.nextSibling != node:  # find predecessor of node
                    current = current.nextSibling
                current.nextSibling = leftChild
                self.updates += 1
                leftChild.nextSibling = node.nextSibling
                self.updates += 1
                if node.parent.rightChild == node:
                    node.parent.rightChild = leftChild
                    self.updates += 1

            elif node.nextSibling != node:  # node is leaf and has siblings
                while current.nextSibling != node:
                    current = current.nextSibling
                current.nextSibling = node.nextSibling
                self.updates += 1
                if node.parent.rightChild == node:
                    node.parent.rightChild = current
                    self.updates += 1

            else:  # node is leaf and has no siblings
                node.parent.rightChild = None
                self.updates += 1

            node.parent = None
            self.updates += 1
            node.nextSibling = node
            self.updates += 1
            self.buffer += [node]

        if len(self.buffer) > math.ceil(math.log(self.size, 2)):
            (cc2, lc2) = self.clean_buffer()
            compCount += cc2
            linkCount += lc2
        return (compCount, linkCount)

    def pointer_updates(self):
        return self.updates