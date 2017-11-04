import pprint

class flatNode():
	def __init__(self, _operation, _next, _prev, _output, _input1, _input2):
		self.operation = _operation
		self.next = _next
		self.thenNext = None
		self.elseNext = None
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
	def __repr__(self):
		return "Var(" + str(self.name) + ")"

class Stack():
	def __init__(self, _name):
		self.name = _name
	def __str__(self):
		return "Stack(" + str(self.name) + ")"
	def __repr__(self):
		return "Stack(" + str(self.name) + ")"

class Esp():
	def __init__(self):
		pass
	def __str__(self):
		return "%esp"
		
class x86IRNode():
	'''
	def __init__(self, _operation, _var1, _var2, _prev, _next):
		self.operation = _operation
		self.next = _next
		self.prev = _prev
		self.var1 = _var1
		self.var2 = _var2
		self.liveness = set([])
		'''
	def __init__(self, _operation, _var1, _var2):
		self.operation = _operation
		self.var1 = _var1
		self.var2 = _var2
		self.next = None
		self.thenNext = None
		self.elseNext = None
		self.prev = None
		self.liveness = set([])
	def __str__(self):
		return "(" + str(self.operation) + ", " + str(self.var1) + ", " + str(self.var2) + ", " + setToStr(self.liveness) + ")"

def printLLwithIf(node, indent):
	while node != None:
		string = ""
		for i in range(0, indent):
			string += "\t"
		string += str(node)
		print string
		if node.operation == "IfExp":
			string = ""
			for i in range(0, indent):
				string += "\t"
			string += "Then:"
			print string
			printLLwithIf(node.thenNext, indent + 1)
			string = ""
			for i in range(0, indent):
				string += "\t"
			string += "Else:"
			print string
			printLLwithIf(node.elseNext, indent + 1)
		node = node.next

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

def setToStr(set):
	string = "Set("
	first = True
	for i in set:
		if first:
			first = False
		else:
			string += ", "
		string += str(i)
	string += ")"
	return string

def dictToStr(dict):
	string = "{"
	first = True
	for i in dict:
		if first:
			first = False
		else:
			string += ", "
		string += str(i) + " : " + str(dict[i]) + "\n"
	string += "}"
	return string

def newVariable(variables, name):
	if name != None:
		for i in variables:
			if name == variables[i]:
				return i
	ret = Var(str(len(variables)))
	variables[ret] = name
	return ret
