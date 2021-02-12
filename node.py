#!/usr/bin/python3
"""Base object for construction of all heap variants"""


class Node:
	def __init__(self, key):
		"""contains all pointers that might be needed in any implementation.
		Only necessary ones used in each implementation"""
		self.key = key
		self.parent = None
		self.leftChild = None
		self.rightChild = None
		self.nextSibling = None
		self.prevSibling = None
		self.leftOnly = False
		self.rightOnly = False
		
		self.vertex = None  # used for testing with Dijkstra's algorithm

