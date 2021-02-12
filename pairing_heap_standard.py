#!/usr/bin/python3
from node import Node
from pairing_heap_interface import PairingHeapInterface


class PairingHeapStandard(PairingHeapInterface):
	"""standard pairing heap
	performs a left-to-right forward pass, then a backward combining pass to consolidate"""

	def __init__(self, root=None):
		self.root = root

	def make_heap(self):
		# this is equivalent to init
		pass

	def listInorder(self, root):
		if (root is None):
			return []
		return self.listInorder(root.leftChild) + [root.key] + self.listInorder(root.nextSibling)

	def find_min(self):
		if self.root is None:
			return None
		else:
			return self.root

	def insert(self, node):
		""" inserts node by linking to current root,
		returns number of link operations"""
		linkCount = 0
		if self.root is None:
			# heap was empty before
			self.root = node
		else:
			newheap = PairingHeapStandard(node)
			linkCount = self.merge(newheap)
		# print(self.listInorder(self.root))
		return linkCount

	def delete_min(self):
		"""Extracts minimum (current root), consolidates orphaned children.
		returns number of link operations"""
		linkCount = 0  # counts number of linking operations
		minNode = None
		if self.root is None:
			print("Heap was already empty.")
			return (minNode, linkCount)
		elif self.root.leftChild is None:
			# heap contained only one element
			minNode = self.root
			self.root = None
			return (minNode, linkCount)
		elif self.root.leftChild.nextSibling is None:
			# first child has no siblings->first child becomes root
			minNode = self.root
			self.root = self.root.leftChild
			self.root.parent = None
			return (minNode, linkCount)
		else:
			minNode = self.root
			self.root = self.root.leftChild
			current = self.root
			nextSibling = None
			heaps = []
			paired = []
			# left-to-right pairing pass
			while current is not None:  # create heaps of all orphaned children
				nextSibling = current.nextSibling
				heaps += [PairingHeapStandard(current)]
				current.nextSibling = None
				current = nextSibling
			for j in range(0, len(heaps), 2):
				if j == (len(heaps) - 1):  # last one
					paired += [heaps[j]]
				else:
					heap = heaps[j]
					linkCount += heap.merge(heaps[j + 1])  # merge returns its number of link operations
					paired += [heap]
			# combining backwards (right-to-left) pass
			combined = paired[-1]  # start with last (rightmost) tree
			for i in range(len(paired) - 2, -1, -1):
				linkCount += combined.merge(paired[i])  # merge returns its number of link operations
			self.root = combined.root
			self.root.parent = None
		return (minNode, linkCount)

	def merge(self, heap2):
		"""merges heap2 with current heap by linking roots.
		returns number of link operations"""
		linkCount = 0  # counts number of linking operations
		if self.root is None:  # heap is empty
			self.root = heap2.root
		elif heap2.root is None:  # heap 2 is empty
			pass  # this heap is the result
		else:
			# link roots
			if self.root.key <= heap2.root.key:
				heap2.root.nextSibling = self.root.leftChild
				if heap2.root.nextSibling is None:
					heap2.root.parent = self.root
				self.root.leftChild = heap2.root
				linkCount = 1
			else:
				self.root.nextSibling = heap2.root.leftChild
				if self.root.nextSibling is None:
					self.root.parent = heap2.root
				heap2.root.leftChild = self.root
				self.root = heap2.root
				linkCount = 1
		return linkCount

	def decrease_key(self, node, diff):
		"""cuts node with subtree from current place in tree;
		decreases key; links node to root"""
		linkCount = 0
		if self.root == node:
			self.root.key = self.root.key - diff
		else:
			# first step: cut node from heap
			self.unlink_node(node)  # helper function
			# second step: decrease key
			subheap = PairingHeapStandard(node)
			subheap.root.key = subheap.root.key - diff
			# third step: merge back in
			linkCount = self.merge(subheap)
		return linkCount

	def delete(self, node):
		"""removes node with subtree from current place in tree;
		deletes node, consolidating orphaned children;
		links consolidated subtree to root.
		returns number of link operations"""
		if node is None:
			return 0
		if self.root.key == node.key:
			(minNode, lc) = self.delete_min()
			return lc
		else:
			self.unlink_node(node)  # helper function

			subheap = PairingHeapStandard(node)
			linkCount = subheap.delete_min()
			linkCount += self.merge(subheap)
			return linkCount

	def unlink_node(self, node):
		"""removes node from heap, updating pointers accordingly"""
		if self.root == node:  # remove the whole heap
			self.root = None
		else:
			if node.nextSibling != None:
				temp = node.nextSibling
				while temp.nextSibling != None:
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
