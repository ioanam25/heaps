#!/usr/bin/python3
class Node:
	def __init__(self, key):
	#for now contains all pointers that might be needed in any implementation
	#idea is to use only necessary ones in each implementation
		self.key = key
		self.parent = None
		self.leftChild = None
		self.rightChild=None
		self.nextSibling=None
		self.prevSibling=None
		self.leftOnly=False
		self.rightOnly=False
		
		self.vertex=None #for testing with Dijkstra's algorithm

