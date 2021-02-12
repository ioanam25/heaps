#!/usr/bin/python3
from node import Node
from pairing_heap_interface import PairingHeapInterface

class PairingHeapStandard(PairingHeapInterface):
	#performs a left-to-right forward pass, then a backward combining pass
	#TODO: left/right child (page 115)
	def __init__(self, root=None):
		self.root=root

	def make_heap(self):
		#this is equivalent to init
		pass
	
	def listInorder(self, root):
		if(root==None):
			return []
		return self.listInorder(root.leftChild)+[root.key]+self.listInorder(root.nextSibling)

	def find_min(self):
		if self.root==None:
			return None
		else:
			return self.root

	def insert(self, node):
		#inserts node as child of root, returns number of link operations
		linkCount=0
		#print("trying to insert {}...".format(node.key))
		if self.root==None: 
			#heap was empty before
			self.root=node
		else:
			newheap=PairingHeapStandard(node)
			linkCount=self.merge(newheap)
		#print(self.listInorder(self.root))
		return linkCount

	def delete_min(self):
		#print("trying to delete min...")
		linkCount=0 #counts number of linking operations
		minKey=None
		minNode=None
		if self.root==None:
			print("Heap was already empty.")
			return (minNode,linkCount)
		elif self.root.leftChild==None:
			#heap contained only one element
			minNode=self.root
			self.root=None
			return (minNode, linkCount)
		elif self.root.leftChild.nextSibling==None:
			#first child has no siblings->first child becomes root
			minNode=self.root
			self.root=self.root.leftChild
			self.root.parent=None
			return (minNode, linkCount)
		else:
			minNode=self.root
			self.root=self.root.leftChild
			current=self.root
			nextSibling=None
			heaps=[]
			paired=[]
			#left-to-right pairing pass v2
			while current!=None:#create heaps of all orphaned children
				nextSibling=current.nextSibling
				heaps+=[PairingHeapStandard(current)]
				current.nextSibling=None
				current=nextSibling
			for j in range(0,len(heaps),2):
				if(j==len(heaps)-1):#last one
					paired+=[heaps[j]]
				else:
					heap=heaps[j]
					linkCount+=heap.merge(heaps[j+1])#merge returns its number of link operations
					paired+=[heap]
			#combining backwards pass v2
			combined=paired[-1]#start with last tree
			for i in range(len(paired)-2, -1, -1):
				linkCount+=combined.merge(paired[i])#merge returns its number of link operations
			self.root=combined.root
			self.root.parent=None
		#print("result is {}".format(self.listInorder(self.root)))	
		return (minNode, linkCount)

	def merge(self, heap2):
		linkCount=0 #counts number of linking operations
		#print("Trying to merge {} and {}...".format(self.listInorder(self.root), self.listInorder(heap2.root)))
		if self.root==None:#heap is empty
			self.root=heap2.root
		elif heap2.root==None:#heap 2 is empty
			pass #this heap is the result
		else:
			if self.root.key<=heap2.root.key:
				heap2.root.nextSibling=self.root.leftChild
				if heap2.root.nextSibling==None:
					heap2.root.parent=self.root
				self.root.leftChild=heap2.root
				linkCount=1
			else:
				self.root.nextSibling=heap2.root.leftChild
				if self.root.nextSibling==None:
					self.root.parent=heap2.root
				heap2.root.leftChild=self.root
				self.root=heap2.root
				linkCount=1
			#TODO check for only children?
		#print("Result is {}".format(self.listInorder(self.root)))
		return linkCount

	def decrease_key(self, node, diff):#TODO more testing
		linkCount=0
		if self.root==node:
			self.root.key=self.root.key-diff
		else:
			#first step: cut node from heap
			self.unlink_node(node)#helper function
			#second step: decrease key
			subheap=PairingHeapStandard(node)
			subheap.root.key=subheap.root.key-diff
			#third step: merge back in
			linkCount = self.merge(subheap)
		return linkCount

	def delete(self, node): #TODO more testing?
		print("trying to delete {} from {}".format(node.key, self.listInorder(self.root)))
		if self.root.key==node.key:
			self.delete_min()
		else:
			self.unlink_node(node)#helper function
					
			subheap=PairingHeapStandard(node)
			subheap.delete_min()
			self.merge(subheap)
		print("result is {}".format(self.listInorder(self.root)))
		pass

	def unlink_node(self, node):
		#removes node from heap updating pointers
		if self.root==node:#remove the whole heap
			self.root=None
		else:
			if node.nextSibling!=None:
				temp=node.nextSibling
				while temp.nextSibling!=None:
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
		
			
