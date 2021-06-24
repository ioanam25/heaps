#!/usr/bin/python3
"""interface implemented by all heap variants"""

class PairingHeapInterface:
	def __init__(self):
		self.count = 0

	def make_heap(self):
		pass
	
	def find_min(self):
		pass

	def insert(self, node):
		pass

	def delete_min(self):
		pass
		
	def merge(self, heap2):
		pass

	def delete(self, node):
		pass

	def pointer_updates(self):
		pass