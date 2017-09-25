class flatNode():
	def __init__(self, _operation, _next, _prev, _output, _input1, _input2):
		self.operation = _operation
		self.next = _next
		self.prev = _prev
		self.output = _output
		self.input1 = _input1
		self.input2 = _input2
	def __str__(self):
		return "(" + str(self.operation) + ", " + str(self.output) + ", " + str(self.input1) + ", " + str(self.input2) + ")"
		
class Var():
	def __init__(self, _name):
		self.name = _name
	def __str__(self):
		return "Var(" + str(self.name) + ")"
		
class x86IRNode():
	def __init__(self, _operation, _var1, _var2, _prev, _next):
		self.operation = _operation
		self.next = _next
		self.prev = _prev
		self.var1 = _var1
		self.var2 = _var2
	def __init__(self, _operation, _var1, _var2):
		self.operation = _operation
		self.var1 = _var1
		self.var2 = _var2
		self.next = None
		self.prev = None
	def __str__(self):
		return "(" + str(self.operation) + ", " + str(self.var1) + ", " + str(self.var2) + ")"


def printLinkedList(node):
	while node != None:
		print node
		node = node.next

def getLast(node):
	if node != None:
		while node.next != None:
			node = node.next
	return node
	
def getFirst(node):
	if node != None:
		while node.prev != None:
			node = node.prev
	return node
