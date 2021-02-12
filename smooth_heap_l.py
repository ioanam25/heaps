#!/usr/bin/python3
from node import Node
import math
from pairing_heap_interface import PairingHeapInterface

class SmoothHeapL(PairingHeapInterface):
	forest=[] #list storing roots of all top-level trees not in buffer
	minNode=None

	def __init__(self, root=None):
		self.forest=[]
		if root!=None:
			root.parent=None
			root.nextSibling=root
			self.minNode=root
			self.forest+=[root]

	def make_heap(self):
		#this is equivalent to init
		pass
	
	def find_min(self):
		return self.minNode
		
	def listPreOrderHelper(self, root):
		res=[]
		if root.rightChild==None:
			return [root.key]
		else:
			current=root.rightChild
			res+=[root.key, self.listPreOrderHelper(current)]
			while current.nextSibling!=root.rightChild:
				current=current.nextSibling
				res+=[self.listPreOrderHelper(current)]
			return [res]
		
	def listPreOrder(self):
		res=[]
		buf=[]
		for item in self.forest:
			res+=self.listPreOrderHelper(item)
		print(res)
		
	def stable_link_left(self, left, right):
		#left node becomes parent of right node
		#print("left-linking nodes {} and {}".format(left.key, right.key))
		if left.rightChild!=None:
			right.nextSibling = left.rightChild.nextSibling
			left.rightChild.nextSibling=right
		else:
			right.nextSibling = right
		left.rightChild=right
		right.parent=left
		
	def stable_link_right(self, left, right):
		#right node becomes parent of left node
		if right.rightChild==None:
			right.rightChild=left
			left.nextSibling=left
		else:
			left.nextSibling=right.rightChild.nextSibling
			right.rightChild.nextSibling=left
		left.parent=right

	def insert(self, node):
		#concatenates node to list of trees in pool
		if node==None:
			return (0,0)#no comparisons, no links
		node.nextSibling=node
		node.parent=None
		self.forest+=[node]
		#if self.minNode==None or node.key<self.minNode.key:
		#	self.minNode=node
		#print("Result of insert is {}.".format(self.listInorder()))
		return (0, 0)#1 comparison, no links

	def merge(self, heap2):
		if heap2==None:
			return(0,0)
		compCount=0
		linkCount=0
		if len(self.forest)>len(heap2.forest):
			#first heap larger than second
			self.forest+=heap2.forest
		else:
			self.forest=heap2.forest+self.forest
		#if(self.minNode.key>heap2.minNode.key):
 		#	self.minNode=heap2.minNode
		return (compCount, linkCount)#TODO add 1 if comparing minnode

	def delete_min(self):
		if (len(self.forest)==0):
			return(None,0,0)
		(cc, lc)=self.treapify()
		assert len(self.forest)==1
		minKey = self.minNode.key
		minKeyNode = self.minNode
		minNodeChildren=[]
		
		if self.minNode.rightChild!=None:
			minNodeChildren+=[self.minNode.rightChild]
			self.minNode.rightChild.parent=None
			current=self.minNode.rightChild.nextSibling
			self.minNode.rightChild.nextSibling=self.minNode.rightChild
			
			while current!=self.minNode.rightChild:
				minNodeChildren+=[current]
				tempNode = current
				current=current.nextSibling
				tempNode.nextSibling = tempNode
				tempNode.parent = None
		self.forest = minNodeChildren
		#print('###')
		#print(minKeyNode.key)
		return (minKeyNode, cc, lc)

	def treapify(self):
		#links roots in pool (forest) into treap and returns number of links/comparisons
		#this uses the pseudocode of delete-min from https://arxiv.org/abs/1802.05471
		linkCount=0#counts only number of links
		compCount=0#counts only number of comparisons
		fs = len(self.forest)
		if len(self.forest)==0: #pool is empty
			self.minNode=None
			return (compCount, linkCount)
			
		elif len(self.forest)==1:
			self.minNode=self.forest[0]
			return (compCount, linkCount)
			
		else:
			i=0
			curr_forest=self.forest
			while i<len(curr_forest)-1:
				compCount+=1#first if-else comparison
				if curr_forest[i].key<curr_forest[i+1].key:
					i=i+1
				else:
					skip=False
					while i>0:
						compCount+=1
						linkCount+=1
						if curr_forest[i-1].key>curr_forest[i+1].key:
							#stable-link predecessor as parent of current node
							self.stable_link_left(curr_forest[i-1], curr_forest[i])
							#remove node at index i from top-list
							curr_forest=curr_forest[:i]+curr_forest[i+1:]
							i=i-1
						else:
							#stable-link successor as parent of current node
							self.stable_link_right(curr_forest[i], curr_forest[i+1])
							#remove node at index i from top-list
							curr_forest=curr_forest[:i]+curr_forest[i+1:]
							#i=i+1
							skip=True
							break
					if not skip:#i==0
						#stable-link current as leftmost child of successor
						self.stable_link_right(curr_forest[i], curr_forest[i+1])
						#remove node from top-list
						curr_forest=curr_forest[i+1:]
						linkCount+=1

			while i>0:
				#stable-link predecessor as parent of current node
				self.stable_link_left(curr_forest[i-1], curr_forest[i])
				curr_forest=curr_forest[:i]
				linkCount+=1
				i=i-1
			self.forest=curr_forest
			assert len(self.forest)==1
			self.minNode=self.forest[0]
		assert(fs-1 == linkCount)
		return (compCount, linkCount)
		
        
	def mergesort(self, llist):
		#standard mergesort, implemented to count comparisons properly
		if len(llist)<2:
			return 0, llist
		split_idx = int(math.floor(len(llist)/2))
		compsleft, lleft = self.mergesort(llist[:split_idx])
		compsright, lright = self.mergesort(llist[split_idx:])
		l=0
		r=0
		comps = compsleft+compsright
		sorted = []
		while l+r<len(llist):
			if r==len(lright) or (l<len(lleft) and lleft[l].key<=lright[r].key):
				sorted+=[lleft[l]]
				l+=1
			else:
				sorted+=[lright[r]]
				r+=1
			comps+=1
		return comps, sorted

	def decrease_key(self, node, diff):
		assert node!=None
		node.key = node.key-diff
		
		#concatenates node to list of trees in pool

		if node.parent==None: #node is a root and has children
			if node in self.forest:
				pass #leave in-place
			else:
				self.listPreOrder()
				raise Exception("node with key {} is not in heap".format(node.key))
		else:#node is not a root
			
			if node.nextSibling==node:#node has no siblings
				node.parent.rightChild=None
								
			else:#node has siblings
				current=node.nextSibling
				while current.nextSibling!=node:#find predecessor of node
					current=current.nextSibling
				current.nextSibling=node.nextSibling
				if node.parent.rightChild==node:
					node.parent.rightChild=current
		
			node.parent=None
			node.nextSibling=node
			self.forest+=[node]
		return (0, 0)
