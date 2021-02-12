#!/usr/bin/python3
from node import Node
from pairing_heap_interface import PairingHeapInterface
from pairing_heap_standard import PairingHeapStandard
from smooth_heap import SmoothHeap
from pairing_heap_l import PairingHeapL
from smooth_heap_l import SmoothHeapL

COUNT_TYPE_LINKS=-1
COUNT_TYPE_COMPS=-2
COUNT_TYPE_BOTH=0

class PairingHeap(PairingHeapInterface):
	MODES={21:"Pairing_L", 22:"Smooth_L"}
	mode=0
	countType=COUNT_TYPE_COMPS
	heap=None
	def __init__(self, mode=0, countType=COUNT_TYPE_COMPS):
		self.mode=mode
		self.countType=countType

	def make_heap(self):
		if self.mode==0:
			self.heap=PairingHeapStandard()
		elif self.mode==12:
			self.heap=SmoothHeap()
		elif self.mode==21:#root list version, everything lazy, to be used for Dijkstra test in paper
			self.heap=PairingHeapL()
		elif self.mode==22:#root list version, everything lazy, to be used for Dijkstra test in paper
			self.heap=SmoothHeapL()
		else:
			raise Exception("Invalid heap ID! No heap of type ID {} is implemented.")
	
	def find_min(self):
		#Careful! Implementation is inconsistent across pairing heap types.
		return self.heap.find_min()

	def insert(self, node):
		#inserts node; returns number of linking operations performed
		result=self.heap.insert(node)
		if isinstance(result, tuple):
			if self.countType==COUNT_TYPE_BOTH:
				return (result[0], result[1])#(comps, links)
			else:
				return result[2+self.countType]
		else:#result should be single number iff link count and comp count are the same
			if self.countType==COUNT_TYPE_BOTH:
				return (result, result)
			else:
				return result

	def delete_min(self):
		#deletes min; returns number of linking operations/comparisons performed
		result=self.heap.delete_min()
		if len(result)==3:
			if self.countType==COUNT_TYPE_BOTH:
				return (result[0], result[1], result[2])#min, comps, links
			else:
				return (result[0],result[3+self.countType])
		else:#result should be 2-tuple iff link count and comp count are the same
			if self.countType==COUNT_TYPE_BOTH:
				return (result[0], result[1], result[1])
			else:
				return result
		
	def merge(self, heap2):
		#merges this heap and heap 2; returns number of linking operations performed
		result = self.heap.merge(heap2)
		if isinstance(result, tuple):
			if self.countType==COUNT_TYPE_BOTH:
				return (result[0], result[1])#(comps, links)
			else:
				return result[2+self.countType]
		else:#result should be single number iff link count and comp count are the same
			if self.countType==COUNT_TYPE_BOTH:
				return (result, result)
			else:
				return result

	def delete(self, node):
		self.heap.delete(node)

	def decrease_key(self, node, diff):
		result = self.heap.decrease_key(node, diff)
		if isinstance(result, tuple):
			if self.countType==COUNT_TYPE_BOTH:
				if result[0]==None or result[1]==None:
					print("heap {} returns None".format(self.MODES[self.mode]))
				return (result[0], result[1])#(comps, links)
			else:
				return result[2+self.countType]
		else:#result should be single number iff link count and comp count are the same
			if self.countType==COUNT_TYPE_BOTH:
				if result==None:
					print("heap {} returns None".format(self.MODES[self.mode]))
				return (result, result)
			else:
				return result
