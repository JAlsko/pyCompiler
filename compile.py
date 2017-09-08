#!/usr/bin/python

import sys
import compiler
from compiler.ast import *

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

def getLast(node):
	while node.next != None:
		node = node.next
	return node
	
def newVariable(variables, name):
	if name != None:
		for i in variables:
			if name == variables[i]:
				return i
	ret = Var(len(variables))
	variables[ret] = name
	return ret

def flattenRecurs(ast, variables):
	if isinstance(ast, Module):
		return flattenRecurs(ast.node, variables)
	elif isinstance(ast, Stmt):
		first = None
		last = None
		for statement in ast.nodes:
			result = flattenRecurs(statement, variables)
			if first == None:
				first = result
				last = getLast(first)
			else:
				last.next = result
				result.prev = last
				last = getLast(last)
		last.next = flatNode("FunctionEnd", None, last, None, len(variables), None)
		return flatNode("FunctionStart", first, None, None, len(variables), None)
	elif isinstance(ast, Printnl):
		result = flattenRecurs(ast.nodes[0], variables)
		if result[0] == None:
			first = flatNode("Print", None, None, None, result[1], None)
		else:
			first = result[0]
			last = getLast(first)
			node = flatNode("Print", None, last, None, result[1], None)
			last.next = node
		return first
	elif isinstance(ast, Assign):
		result = flattenRecurs(ast.expr, variables)
		output = flattenRecurs(ast.nodes[0], variables)
		if result[0] == None:
			first = flatNode("Assign", None, None, output, result[1], None)
		else:
			first = result[0]
			last = getLast(first)
			node = flatNode("Assign", None, last, output, result[1], None)
			last.next = node
		return first
		
	elif isinstance(ast, AssName):
		return newVariable(variables, ast.name)
	elif isinstance(ast, Discard):
		return flattenRecurs(ast.expr, variables)[0]
	elif isinstance(ast, Const):
		return None, ast.value
	elif isinstance(ast, Name):
		for i in variables:
			if variables[i] == ast.name:
				return None, i
	elif isinstance(ast, Add):
		leftTuple = flattenRecurs(ast.left, variables)
		left = leftTuple[0]
		rightTuple = flattenRecurs(ast.right, variables)
		right = rightTuple[0]
		first = None
		output = newVariable(variables, None)
		if left != None:
			first = left
			last = getLast(left)
		if right != None:
			if first == None:
				first = right
			else:
				right.prev = last
				last.next = right
			last = getLast(right)
		if first == None:
			first = flatNode("Add", None, None, output, leftTuple[1], rightTuple[1])
		else:
			last.next = flatNode("Add", None, last, output, leftTuple[1], rightTuple[1])
		return (first, output)
		
	elif isinstance(ast, UnarySub):
		result = flattenRecurs(ast.expr, variables)
		output = newVariable(variables, None)
		if result[0] == None:
			first = flatNode("Neg", None, None, output, result[1], None)
		else:
			first = result[0]
			last = getLast(first)
			node = flatNode("Neg", None, last, output, result[1], None)
			last.next = node
		return first, output
	elif isinstance(ast, CallFunc):
		if ast.node.name == 'input':
			output = newVariable(variables, None)
			return flatNode("Input", None, None, output, None, None), output
			
	else:
		raise Exception("No AST match: " + str(ast))
	
def flatten(ast):
	variables = {}
	return flattenRecurs(ast, variables)

def printLinkedList(node):
	while node != None:
		print node
		node = node.next
		
def createAssembly(targetFile, flatAst):
	with open(targetFile, "w") as outputFile:
		node = flatAst
		while node != None:
			if node.operation == "FunctionStart":
				outputFile.write("pushl %ebp\n")
				outputFile.write("movl %esp, %ebp\n")
				outputFile.write("subl $" + str(node.input1* 4) + ", %esp\n")
			elif node.operation == "FunctionEnd":
				outputFile.write("addl $" + str(node.input1* 4) + ", %esp\n")
				outputFile.write("movl $0, %eax\n")
				outputFile.write("leave\n")
				outputFile.write("ret\n")
			elif node.operation == "Print":
				outputFile.write("pushl %eax\n")
				outputFile.write("call print_int_nl\n")
			elif node.operation == "Assign":
				if isinstance(node.input1, Var):
					outputFile.write("movl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
					outputFile.write("movl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
				else:
					outputFile.write("movl $" + str(node.input1) + ", -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Add":
				if isinstance(node.input1, Var):
					outputFile.write("movl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("movl $" + str(node.input1) + ", %eax\n")
				if isinstance(node.input2, Var):
					outputFile.write("addl -" + str((node.input2.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("addl $" + str(node.input2) + ", %eax\n")
				outputFile.write("movl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Neg":
				if isinstance(node.input1, Var):
					outputFile.write("movl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("movl $" + str(node.input1) + ", %eax\n")
				outputFile.write("negl %eax\n")
				outputFile.write("movl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Input":
				outputFile.write("call input\n")
				outputFile.write("movl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			else:
				raise Exception("No flatAST match: " + str(node))
			
			node = node.next
		outputFile.close()

def main():
	with open(sys.argv[1], "r") as inputFile:
		ast = compiler.parse(inputFile.read())
		inputFile.close()
		print ast
		flatAst = flatten(ast)
		printLinkedList(flatAst)
		print sys.argv[1]
		print sys.argv[1][:-2] + "s"
		createAssembly(sys.argv[1][:-2] + "s", flatAst)
		
		
main()
