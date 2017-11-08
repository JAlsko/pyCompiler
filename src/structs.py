import pprint
import sys
import compiler
from compiler.ast import *
from eStructs import *

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
		elif node.operation == "While":
			string = ""
			for i in range(0, indent):
				string += "\t"
			string += "Do:"
			print string
			printLLwithIf(node.thenNext, indent + 1)
		node = node.next

def indentPrint(str, indents):
	string = ""
	for i in range(0, indents):
		string += "\t"
	print string + str

def astReadable(ast):
	input = str(ast)
	indent = 0
	output = ""
	unit = False
	i = 0
	while i < len(input):
		if input[i] == " ":
			pass
		elif input[i] in  ['(', '[', '{']:
			output += input[i]
			if (i > 4) and input[i-4:i] in ["Bool", "Name"]:
				unit = True
			elif (i > 5) and input[i-5:i] in ["Const"]:
				unit = True
			else:
				output += '\n'
				indent += 1
				for j in range(0, indent):
					output += "|  "
		elif input[i] in [')', ']', '}']:
			output += input[i]
			if unit == True:
				unit = False
			else:
				indent -= 1
				if not ((i+1 < len(input)) and input[i+1] in [',', ':']):
					output += '\n'
					for j in range(0, indent):
						output += "|  "
		elif input[i] in [',', ':']:
			output += input[i]
			if unit == True:
				pass
			else:
				output += "\n"
				for j in range(0, indent):
					output += "|  "
		else:
			output += input[i]
		i += 1
	return output

def printAst(ast, indents):
	if isinstance(ast, Module):
		indentPrint("Module(", indents)
		printAst(ast.node, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Stmt):
		indentPrint("Stmt(", indents)
		printAst(ast.nodes, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Printnl):
		indentPrint("Printnl(", indents)
		printAst(ast.nodes, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Assign):
		indentPrint("Assign(", indents)
		printAst(ast.nodes, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.expr, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, AssName):
		indentPrint("AssName(", indents)
		printAst(ast.name, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.flags, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Discard):
		indentPrint("Discard(", indents)
		printAst(ast.expr, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Const):
		indentPrint("Const(", indents)
		indentPrint(str(ast.value), indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Bool):
		indentPrint("Bool(", indents)
		indentPrint(str(ast.value), indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Name):
		indentPrint("Name(", indents)
		printAst(ast.name, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Add):
		indentPrint("Add(", indents)
		printAst(ast.left, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.right, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Compare):
		indentPrint("Compare(", indents)
		printAst(ast.expr, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.ops, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, UnarySub):
		indentPrint("UnarySub(", indents)
		printAst(ast.expr, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Not):
		indentPrint("Not(", indents)
		printAst(ast.expr, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, CallFunc):
		indentPrint("CallFunc(", indents)
		printAst(ast.node, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.args, indents+1)
		indentPrint(")", indents+1)
	elif isinstance(ast, List):
		indentPrint("List(", indents)
		printAst(ast.nodes, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, list):
		indentPrint("[", indents)
		for node in ast:
			printAst(node, indents)
			indentPrint(",", indents)
		indentPrint("]", indents)
	elif isinstance(ast, Dict):
		indentPrint("Dict(", indents)
		printAst(ast.items, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, tuple):
		indentPrint("(", indents)
		for node in ast:
			printAst(node, indents+1)
			indentPrint(",", indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, dict):
		indentPrint("{", indents)
		for key in ast:
			indentPrint(key + ":", indents)
			printAst(ast[key], indents+1)
			indentPrint(",", indents)
		indentPrint("}",indents)
	elif isinstance(ast, IfExp):
		indentPrint("IfExp(", indents)
		printAst(ast.test, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.then, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.else_, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Let):
		indentPrint("Let(", indents)
		printAst(ast.var, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.rhs, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.body, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, InjectFrom):
		indentPrint("InjectFrom(", indents)
		printAst(ast.typ, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.arg, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, ProjectTo):
		indentPrint("ProjectTo(", indents)
		printAst(ast.typ, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.arg, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, GetTag):
		indentPrint("GetTag(", indents)
		printAst(ast.arg, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Lambda):
		indentPrint("Lambda(", indents)
		printAst(ast.argnames, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.code, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Function):
		indentPrint("Function(", indents)
		printAst(ast.name, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.argnames, indents+1)
		indentPrint(",", indents+1)
		printAst(ast.code, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, GlobalFuncName):
		indentPrint("GlobalFuncName(", indents)
		printAst(ast.name, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, Return):
		indentPrint("Return(", indents)
		printAst(ast.value, indents+1)
		indentPrint(")", indents)
	elif isinstance(ast, str):
		indentPrint(ast, indents)
	else:
		raise Exception("No AST match: " + str(ast))

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
