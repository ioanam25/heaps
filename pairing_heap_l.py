#!/usr/bin/python3
from node import Node
from pairing_heap_interface import PairingHeapInterface


class PairingHeapL(PairingHeapInterface):
    """lazy variant of standard pairing heap
    (maintaining root-list and consolidating only upon extract-min)"""
    forest = []  # list storing roots of all top-level trees
    updates = 0

    def __init__(self, root=None):
        self.forest = []
        if root is not None:
            root.parent = None
            self.updates += 1
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
        self.updates += 1
        self.forest += [node]
        return 0

    def pairing(self):
        """performs consolidation (left-to-right pairing pass, linking pairs of neighbours,
         followed by right-to-left combining) and returns number of linking operations"""
        fs = len(self.forest)
        if fs < 2:
            return 0
        else:
            # right-to-left-pairing pass
            pairedForest = []
            for i in range(0, fs, 2):
                if i == fs - 1:  # last tree if length of forest is odd-numbered
                    pairedForest += [self.forest[i]]  # concatenate to new forest (no linking required)
                else:  # link neighbouring roots
                    if self.forest[i].key <= self.forest[i + 1].key:
                        if self.forest[i].leftChild == None:
                            self.forest[i + 1].parent = self.forest[i]
                            self.updates += 1
                        else:
                            self.forest[i + 1].nextSibling = self.forest[i].leftChild
                            self.updates += 1
                        self.forest[i].leftChild = self.forest[i + 1]
                        self.updates += 1
                        pairedForest += [self.forest[i]]
                    else:
                        if self.forest[i + 1].leftChild == None:
                            self.forest[i].parent = self.forest[i + 1]
                            self.updates += 1
                        else:
                            self.forest[i].nextSibling = self.forest[i + 1].leftChild
                            self.updates += 1
                        self.forest[i + 1].leftChild = self.forest[i]
                        self.updates += 1
                        pairedForest += [self.forest[i + 1]]
            self.forest = pairedForest

            # right-to-left combining pass
            index = len(self.forest) - 1
            for i in range(len(self.forest) - 2, -1, -1):  # link two rightmost roots
                if self.forest[index].key <= self.forest[i].key:
                    if self.forest[index].leftChild == None:
                        self.forest[i].parent = self.forest[index]
                        self.updates += 1
                    else:
                        self.forest[i].nextSibling = self.forest[index].leftChild
                        self.updates += 1
                    self.forest[index].leftChild = self.forest[i]
                    self.updates += 1
                else:
                    if self.forest[i].leftChild == None:
                        self.forest[index].parent = self.forest[i]
                        self.updates += 1
                    else:
                        self.forest[index].nextSibling = self.forest[i].leftChild
                        self.updates += 1
                    self.forest[i].leftChild = self.forest[index]
                    self.updates += 1
                    index = i

            self.forest = [self.forest[index]]
            return (fs - 1)  # number of links needed to consolidate n roots is n-1

    def delete_min(self):
        """finds and deletes min; restructures forest; returns number of linking operations"""
        cn = self.pairing()
        assert len(self.forest) == 1
        currentSibling = self.forest[0].leftChild
        while currentSibling != None:
            nextSibling = currentSibling.nextSibling
            self.forest += [currentSibling]
            currentSibling.nextSibling = None
            self.updates += 1
            currentSibling = nextSibling
        self.forest[-1].parent = None  # only for the last concatenated sibling as only this one carried parent pointer
        self.updates += 1
        minNode = self.forest[0]
        self.forest = self.forest[1:]
        return (minNode, cn, cn)

    def decrease_key(self, node, diff):
        """unlinks node from current position in tree (if inner node),
        decreases key, adds node with subtree to root list"""
        if node is None or diff <= 0:
            return 0
        elif node.parent is None and node.nextSibling is None:  # node is root
            node.key = node.key - diff
            self.updates += 1
        else:
            self.unlink_node(node)
            node.key = node.key - diff
            self.updates += 1
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
                self.updates += 1
            else:
                self.forest[-1].parent = None
                self.updates += 1
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
                    self.updates += 1
                    node.nextSibling = None
                    self.updates += 1
                else:
                    # node is neither first nor last child of parent
                    prevSibling = temp.parent.leftChild
                    while prevSibling.nextSibling != node:  # find left (previous) sibling
                        prevSibling = prevSibling.nextSibling
                    prevSibling.nextSibling = node.nextSibling  # cut out node, link left and right sibling
                    self.updates += 1
                    node.nextSibling = None
                    self.updates += 1
            else:
                # node is rightmost child of parent
                if node.parent.leftChild == node:
                    # node is only child: just remove
                    node.parent.leftChild = None
                    self.updates += 1
                else:
                    prevSibling = node.parent.leftChild
                    while prevSibling.nextSibling != node:  # find left (previous) sibling
                        prevSibling = prevSibling.nextSibling
                    prevSibling.parent = node.parent
                    self.updates += 1
                    prevSibling.nextSibling = None
                    self.updates += 1
            node.parent = None
            self.updates += 1

    def pointer_updates(self):
        return self.updates