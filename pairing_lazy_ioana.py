#!/usr/bin/python3
from node import Node
from pairing_heap_interface import PairingHeapInterface


class PairingHeapLazy(PairingHeapInterface):
    """lazy variant of standard pairing heap
    (maintaining root-list and min-root pointer and consolidating only upon extract-min)"""
    forest = []  # list storing roots of all top-level trees
    minNode = None
    minNodeIndex = -1

    def __init__(self, root=None):
        self.forest = []
        if root is not None:
            root.parent = None
            self.forest += [root]

    def listInorder(self):
        forestList = []
        for root in self.forest:
            forestList += [self.listInorderTree(root)]
        return forestList

    def listInorderTree(self, root):
        if root is None:
            return []
        else:
            return self.listInorderTree(root.leftChild) + [root.key] + self.listInorderTree(root.nextSibling)

    def insert(self, node):
        # concatenates node to list of trees; returns number of linking ops (always 0) for sake of consistency
        # print("trying to insert {}...".format(node.key))
        if node is None:
            return 0
        node.parent = None
        self.forest += [node]
        if self.minNode is None or node.key <= self.minNode.key:
            self.minNode = node
            self.minNodeIndex = len(self.forest) - 1
        return 0

    def pairing(self):
        """performs consolidation left-to-right pairing pass, linking pairs of neighbours,
          and returns current minimum and number of linking operations"""
        fs = len(self.forest)
        if fs < 2:
            currentMin = self.forest[0]
            return 0
        else:
            # right-to-left-pairing pass
            pairedForest = []
            currentMin = self.forest[0]
            links = 0
            # print(self.listInorder())
            for i in range(0, fs, 2):
                if i == fs - 1:  # last tree if length of forest is odd-numbered
                    if self.forest[i].key < currentMin.key:
                        currentMin = self.forest[i]
                    pairedForest += [self.forest[i]]  # concatenate to new forest (no linking required)
                else:  # link neighbouring roots
                    if self.forest[i].key <= self.forest[i + 1].key:
                        if self.forest[i].leftChild == None:
                            self.forest[i + 1].parent = self.forest[i]
                        else:
                            self.forest[i + 1].nextSibling = self.forest[i].leftChild
                        self.forest[i].leftChild = self.forest[i + 1]
                        if self.forest[i].key < currentMin.key:
                            currentMin = self.forest[i]
                        # print(self.forest[i])
                        pairedForest += [self.forest[i]]
                    else:
                        if self.forest[i + 1].leftChild == None:
                            self.forest[i].parent = self.forest[i + 1]
                        else:
                            self.forest[i].nextSibling = self.forest[i + 1].leftChild
                        self.forest[i + 1].leftChild = self.forest[i]
                        if self.forest[i + 1].key < currentMin.key:
                            currentMin = self.forest[i + 1]
                        # print(self.forest[i + 1])
                        pairedForest += [self.forest[i + 1]]
            self.forest = pairedForest
            # print(self.listInorder())
            self.minNode = currentMin
            self.minNodeIndex = self.forest.index(self.minNode)
            # print("index is ", self.minNodeIndex)
            # print("forest length is ", len(self.forest))
            return (fs / 2)  # number of links needed to consolidate n roots

    def find_min(self):
        return self.minNode

    def delete_min(self):
        # print(self.listInorder())
        if self.minNode == None:
            print("Cannot delete empty heap")
            return

        # print(self.minNode.key)
        index = self.minNodeIndex
        # print("index", index)
        # print("forestsize", len(self.forest))
        currentSibling = self.forest[index].leftChild
        oldMinNode = self.minNode

        # remove minNode from forest
        # print("index removed", index)
        if index == 0:
            self.forest = self.forest[1:]
        elif index == len(self.forest) - 1:
            self.forest = self.forest[:index]
        else:
            self.forest = self.forest[:index] + self.forest[(index + 1):]

        # move all children of deleted root in front of the other roots
        while currentSibling != None:
            nextSibling = currentSibling.nextSibling
            self.forest.insert(0, currentSibling)
            currentSibling.nextSibling = None
            # print(self.forest[0])
            self.forest[0].parent = None
            currentSibling = nextSibling

        # print("forest length before pairing", len(self.forest))
        if len(self.forest) > 1:
            cn = self.pairing()
            return (oldMinNode, cn*2, cn)
        elif len(self.forest) == 1:
            self.minNodeIndex = 0
            self.minNode = self.forest[0]
            return (oldMinNode, 0, 0)
        else:
            return (oldMinNode, 0, 0)

    def decrease_key(self, node, diff):
        """unlinks node from current position in tree (if inner node),
        decreases key, adds node with subtree to root list"""
        if node is None or diff <= 0:
            return 0
        elif node.parent is None and node.nextSibling is None:  # node is root
            node.key = node.key - diff
            if node.key < self.minNode.key:
                self.minNode = node
        else:
            self.unlink_node(node)
            node.key = node.key - diff
            if node.key < self.minNode.key:
                self.minNode = node
            self.forest += [node]
        return 0

    def merge(self, heap2):
        """concatenates forests of this heap and heap2; returns number of link operations (always 0) for consistency"""
        self.forest += heap2.forest
        return 0

    def delete(self, node):
        """deletes node from heap; concatenates orphaned children to list of roots"""
        if node is None:
            # print("Cannot delete None")
            return
        elif node.parent is None and node.nextSibling is None:  # node is root
            # print("Trying to delete {}...".format(node.key))
            index = self.forest.index(node)  # slight cheating; would be nicer to use a linked list as forest instead
            # remove node from forest list
            self.forest = self.forest[:index] + self.forest[index + 1:]
        else:  # node is a child somewhere
            # print("Trying to delete {}...".format(node.key))
            self.unlink_node(node)
        # concatenate potential children to forest list
        sibling = node.leftChild
        while sibling is not None:
            self.forest += [sibling]
            sibling = sibling.nextSibling
            if sibling is not None:
                self.forest[-1].nextSibling = None
            else:
                self.forest[-1].parent = None
        print("Result of deletion of {} is {}.".format(node.key, self.listInorder()))

    def unlink_node(self, node):
        """for non-root nodes only: unlinks node from current location, re-establishes links in remaining heap
        (does nothing about forest list, only tree-internal links)"""
        if node == None:
            return
        else:
            if node.nextSibling != None:
                temp = node.nextSibling
                while temp.nextSibling != None:  # find rightmost child
                    temp = temp.nextSibling
                if temp.parent.leftChild == node:  # node is leftmost child
                    # link parent to next sibling
                    temp.parent.leftChild = node.nextSibling
                    node.nextSibling = None
                else:
                    # node is neither first nor last child of parent
                    prevSibling = temp.parent.leftChild
                    while prevSibling.nextSibling != node:  # find left (previous) sibling
                        prevSibling = prevSibling.nextSibling
                    prevSibling.nextSibling = node.nextSibling  # cut out node, link left and right sibling
                    node.nextSibling = None
            else:
                # node is rightmost child of parent
                if node.parent.leftChild == node:
                    # node is only child: just remove
                    node.parent.leftChild = None
                else:
                    prevSibling = node.parent.leftChild
                    while prevSibling.nextSibling != node:  # find left (previous) sibling
                        prevSibling = prevSibling.nextSibling
                    prevSibling.parent = node.parent
                    prevSibling.nextSibling = None
            node.parent = None
