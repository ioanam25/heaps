#!/usr/bin/python3
from node import Node
import math
from pairing_heap_interface import PairingHeapInterface


class PairingSlimHeap(PairingHeapInterface):
    """lazy implementation of slim heap without buffer"""
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

    def link(self, parent, child):
        """child becomes leftmost child of parent"""
        if parent.rightChild is None:
            parent.rightChild = child
            self.updates += 1
            child.nextSibling = child
            self.updates += 1
        else:
            child.nextSibling = parent.rightChild.nextSibling
            self.updates += 1
            parent.rightChild.nextSibling = child
            self.updates += 1
        child.parent = parent
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

    def pairing(self):
        """performs consolidation left-to-right pairing pass, linking pairs of neighbours,
          and returns current minimum and number of linking operations"""
        fs = len(self.forest)
        compCount = 0
        if fs < 2:
            currentMin = self.forest[0]
            return 0, 0
        else:
            # right-to-left-pairing pass
            pairedForest = []
            currentMin = self.forest[0]
            links = 0
            # print("before pairing")
            # print(self.listPreOrder())
            # print(len(self.forest))
            for i in range(0, fs, 2):
                # print(self.forest[i])
                if i == fs - 1:  # last tree if length of forest is odd-numbered
                    if self.forest[i].key < currentMin.key:
                        currentMin = self.forest[i]
                        compCount += 1
                    pairedForest += [self.forest[i]]  # concatenate to new forest (no linking required)
                else:  # link neighbouring roots
                    if self.forest[i].key <= self.forest[i + 1].key:
                        self.link(self.forest[i], self.forest[i + 1])
                        pairedForest += [self.forest[i]]
                    else:
                        self.link(self.forest[i + 1], self.forest[i])
                        pairedForest += [self.forest[i + 1]]
                    compCount += 1

            self.forest = pairedForest
            # print(self.listInorder())
            # self.minNode = currentMin
            self.updates += 1
            # self.minNodeIndex = self.forest.index(self.minNode)
            # print("index is ", self.minNodeIndex)
            # print("forest length is ", len(self.forest))
            # print("after pairing pass")
            # print(len(self.forest))
            # self.listPreOrder()
            return (compCount, fs / 2)  # number of comparisons and links needed to consolidate n roots


    def delete_min(self):
        """consolidates into single tree; extracts min node,
        placing its orphaned children in root list.
        Returns min node, number comparisons, number links"""
        if len(self.forest) == 0:
            return (None, 0, 0)
        # print(type(self.forest))
        # print("forest length is: ", len(self.forest))
        (c1, l1) = self.pairing()
        (cc, lc) = self.treapify()
        assert len(self.forest) == 1
        minKeyNode = self.minNode
        minNodeChildren = []
        # print(minKeyNode.key)

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
        return (minKeyNode, cc + c1, lc + l1)

    def treapify(self):
        """links roots in pool (forest) into treap and returns number of links/comparisons
        this uses the pseudocode of delete-min from https://arxiv.org/abs/1802.05471
        returns number comparisons, number link operations performed"""
        linkCount = 0  # counts only number of links
        compCount = 0  # counts only number of comparisons
        fs = len(self.forest)
        if len(self.forest) == 0:  # pool is empty
            self.minNode = None
            return (compCount, linkCount)

        elif len(self.forest) == 1:
            self.minNode = self.forest[0]
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
                            # link predecessor as parent of current node
                            self.link(curr_forest[i - 1], curr_forest[i])

                            # remove node at index i from top-list
                            curr_forest = curr_forest[:i] + curr_forest[i + 1:]
                            i = i - 1
                        else:
                            # link successor as parent of current node
                            self.link(curr_forest[i + 1], curr_forest[i])
                            # remove node at index i from top-list
                            curr_forest = curr_forest[:i] + curr_forest[i + 1:]
                            # i=i+1
                            skip = True
                            break
                    if not skip:  # i==0
                        # link current as leftmost child of successor
                        self.link(curr_forest[i + 1], curr_forest[i])
                        # remove node from top-list
                        curr_forest = curr_forest[i + 1:]
                        linkCount += 1

            while i > 0:
                # link predecessor as parent of current node
                self.link(curr_forest[i - 1], curr_forest[i])
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
        # print("node.key", node.key, "diff", diff, "expect new key to be", node.key - diff)
        node.key = node.key - diff
        self.updates += 1
        # concatenates node to list of trees in pool
        # self.listPreOrder()
        #print("old node key was", node.key + diff, "new is", node.key)
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


if __name__ == "__main__":
    tree = PairingSlimHeap()
    tree.insert(Node(1))
    tree.insert(Node(10))
    tree.insert(Node(7))
    tree.insert(Node(3))
    node = Node(5)
    tree.insert(node)
    tree.listPreOrder()
    tree.delete_min()
    tree.listPreOrder()
    tree.decrease_key(node, 1)
    tree.delete_min()
    tree.listPreOrder()

