#!/usr/bin/python3
from node import Node
from pairing_heap_interface import PairingHeapInterface

class PairingHeapL(PairingHeapInterface):
	#  lazy variant of standard pairing heap (maintaining root-list and consolidating only upon extract-min)
	forest=[] #list storing roots of all top-level trees
	def __init__(self, root=None):
		self.forest=[]
		if root!=None:
			root.parent=None
			self.forest+=[root]

	def listInorder(self):
		forestList=[]
		for root in self.forest:
			forestList+=[self.listInorderTree(root)]
		return forestList

	def listInorderTree(self, root):
		if root==None:
			return []
		else:
			return self.listInorderTree(root.leftChild)+[root.key]+self.listInorderTree(root.nextSibling)

	def insert(self, node):
		#concatenates node to list of trees; returns number of linking ops (always 0) for sake of consistency
		#print("trying to insert {}...".format(node.key))
		if node==None:
			return 0
		node.parent=None
		self.forest+=[node]
		return 0	

	def pairing(self):
		fs = len(self.forest)
		#performs pairing pass and returns number of linking operations
		linkCount=0
		if fs<2: 
			return 0
		else:
			pairedForest=[]
			index=-1
			for i in range(0, fs, 2): #  pairing pass
				if i==fs-1: #last tree if length of forest is odd-numbered
					pairedForest+=[self.forest[i]]#concatenate to new forest (no linking required)
				else:#pair trees
					if self.forest[i].key<=self.forest[i+1].key:
						if self.forest[i].leftChild==None:
							self.forest[i+1].parent=self.forest[i]
						else:
							self.forest[i+1].nextSibling=self.forest[i].leftChild
						self.forest[i].leftChild=self.forest[i+1]
						pairedForest+=[self.forest[i]]
					else:
						if self.forest[i+1].leftChild==None:
							self.forest[i].parent=self.forest[i+1]
						else:
							self.forest[i].nextSibling=self.forest[i+1].leftChild
						self.forest[i+1].leftChild=self.forest[i]
						pairedForest+=[self.forest[i+1]]
			self.forest=pairedForest
			##print("Result of 1st round {}.".format(self.listInorder()))
			index = len(self.forest)-1
			for i in range(len(self.forest)-2, -1, -1): # combining pass
				if self.forest[index].key<=self.forest[i].key:
					if self.forest[index].leftChild==None:
						self.forest[i].parent=self.forest[index]
					else:
						self.forest[i].nextSibling=self.forest[index].leftChild
					self.forest[index].leftChild=self.forest[i]
				else:
					if self.forest[i].leftChild==None:
						self.forest[index].parent=self.forest[i]
					else:
						self.forest[index].nextSibling=self.forest[i].leftChild
					self.forest[i].leftChild=self.forest[index]
					index=i

			self.forest=[self.forest[index]]
			##print("Result of 2nd round {}.".format(self.listInorder()))
			return (fs-1)

	def delete_min(self):
		#finds and deletes min; restructures forest; returns number of linking operations
		linkCount=0
		compCount=0
		cn = self.pairing()
		assert len(self.forest)==1
		#if (len(self.forest)==0):
		#	print("Cannot delete min of empty heap")
		#	return (None,0,0)
		currentSibling=self.forest[0].leftChild
		while currentSibling!=None:
			nextSibling=currentSibling.nextSibling
			self.forest+=[currentSibling]
			currentSibling.nextSibling=None
			currentSibling=nextSibling
		self.forest[-1].parent=None #only for the last concatenated sibling as only this one carried parent pointer
		minNode = self.forest[0]
		self.forest=self.forest[1:]
		##print("Result of delete-min {}.".format(self.listInorder()))
		###print('**')
		###print(minNode.key)
		return (minNode, cn, cn)

	def decrease_key(self, node, diff):
		linkCount=0
		if node==None or diff<=0:
			return 0
		elif node.parent==None and node.nextSibling==None: #node is root
			node.key=node.key-diff
		else:
			self.unlink_node(node)
			node.key=node.key-diff
			self.forest+=[node]
		return 0

	def merge(self, heap2):
		#concatenates forests of this heap and heap2; returns number of link operations (always 0) for consistency
		#print("Trying to merge {} and {}.".format(self.listInorder(), heap2.listInorder()))
		self.forest+=heap2.forest
		#print("Result of merge is {}.".format(self.listInorder()))
		return 0

	def delete(self, node):
		if node==None:
			print("Cannot delete None")
			return
		elif node.parent==None and node.nextSibling==None: #node is root
			print("Trying to delete {}...".format(node.key))
			index=self.forest.index(node)#slight cheating; would be nicer to use a linked list as forest instead
			#remove node from forest list
			self.forest=self.forest[:index]+self.forest[index+1:]
		else: #node is a child somewhere
			print("Trying to delete {}...".format(node.key))
			self.unlink_node(node)
		#concatenate potential children to forest list
		sibling=node.leftChild
		while sibling!=None:
			self.forest+=[sibling]
			sibling=sibling.nextSibling
			if sibling!=None:
				self.forest[-1].nextSibling=None
			else:
				self.forest[-1].parent=None
		print("Result of deletion of {} is {}.".format(node.key, self.listInorder()))

				
	def unlink_node(self, node):
		#for non-root nodes only (does nothing about forest list, only tree-internal links)
		if node==None:
			return
		else:
			if node.nextSibling!=None:
				temp=node.nextSibling
				while temp.nextSibling!=None:#find rightmost child
					temp=temp.nextSibling
				if temp.parent.leftChild==node:#node is leftmost child 
					#link parent to next sibling
					temp.parent.leftChild=node.nextSibling
					node.nextSibling=None
				else:
					#node is neither first nor last child of parent
					prevSibling=temp.parent.leftChild
					while prevSibling.nextSibling!=node:#find left (previous) sibling
						prevSibling=prevSibling.nextSibling
					prevSibling.nextSibling=node.nextSibling #cut out node, link left and right sibling
					node.nextSibling=None
			else:
				#node is rightmost child of parent
				if node.parent.leftChild==node:
					#node is only child: just remove
					node.parent.leftChild=None
				else:
					prevSibling=node.parent.leftChild
					while prevSibling.nextSibling!=node:#find left (previous) sibling
						prevSibling=prevSibling.nextSibling
					prevSibling.parent=node.parent
					prevSibling.nextSibling=None
			node.parent=None
