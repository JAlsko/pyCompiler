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

def getLast(node):
	while node.next != None:
		node = node.next
	return node

def flattenRecurs(ast, var):
	if isinstance(ast, Module):
		return flattenRecurs(ast.node, None)
	elif isinstance(ast, Stmt):
		first = None
		last = None
		for statement in ast.nodes:
			result = flattenRecurs(statement, None)
			if first == None:
				first = result
				last = getLast(first)
			else:
				last.next = result
				last = getLast(last)
		return first
		
	else:
		raise Exception("No AST match: " + str(ast))
	
def flatten(ast):
	return flattenRecurs(ast, None)

def printLinkedList(node):
	while node != None:
		print str(node.operation) + " " + str(node.output) + " " + str(node.input1) + " " + str(node.input2)
		node = node.next
		

def main():
	with open(sys.argv[1], "r") as inputFile:
		ast = compiler.parse(inputFile.read())
		print ast
		flatAst = flatten(ast)
		print type(ast)
		printLinkedList(flatAst)
main()
