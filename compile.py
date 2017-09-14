#!/usr/bin/python

import sys
import compiler
from compiler.ast import *
import ply.lex as lex
import ply.yacc as yacc

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
		outputFile.write(".globl main\n")
		outputFile.write("main:\n")
		while node != None:
			if node.operation == "FunctionStart":
				outputFile.write("\tpushl %ebp\n")
				outputFile.write("\tmovl %esp, %ebp\n")
				outputFile.write("\tsubl $" + str(node.input1* 4) + ", %esp\n")
			elif node.operation == "FunctionEnd":
				#outputFile.write("\taddl $" + str(node.input1* 4) + ", %esp\n")
				outputFile.write("\tmovl $0, %eax\n")
				outputFile.write("\tleave\n")
				outputFile.write("\tret\n")
			elif node.operation == "Print":
				if isinstance(node.input1, Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", %eax\n")
				outputFile.write("\tpushl %eax\n")
				outputFile.write("\tcall print_int_nl\n")
				outputFile.write("\taddl $4, %esp\n")
			elif node.operation == "Assign":
				if isinstance(node.input1, Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
					outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Add":
				if isinstance(node.input1, Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", %eax\n")
				if isinstance(node.input2, Var):
					outputFile.write("\taddl -" + str((node.input2.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\taddl $" + str(node.input2) + ", %eax\n")
				outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Neg":
				if isinstance(node.input1, Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", %eax\n")
				outputFile.write("\tnegl %eax\n")
				outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Input":
				outputFile.write("\tcall input\n")
				outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			else:
				raise Exception("No flatAST match: " + str(node))
			
			node = node.next
		outputFile.close()

def main():
	with open(sys.argv[1], "r") as inputFile:
		reserved = {'print' : 'PRINT', 'input()' : 'INPUT'}
		tokens = ['INT','PLUS','ASSIGN','PAREN_START','PAREN_END','NEG','NAME'] + list(reserved.values())
		t_PRINT = r'print'
		t_PLUS = r'\+'
		t_NEG = r'\-'
		t_ASSIGN = r'='
		t_INPUT = r'input\(\)'
		t_PAREN_START = r'\('
		t_PAREN_END = r'\)'
		#t_VAR = r'[a-zA-Z_][a-zA-Z0-9_]*'
		def t_NAME(t):
			r'[a-zA-Z_][a-zA-Z_0-9]*'
			t.type = reserved.get(t.value,'NAME')
			return t
		def t_INT(t):
			r'\d+'
			try:
				t.value = int(t.value)
			except ValueError:
				print "integer value too large", t.value
				t.value = 0
			return t
		t_ignore  = ' \t'
		def t_newline(t):
			r'\n+'
			t.lexer.lineno += t.value.count("\n")
		def t_error(t):
			print "Illegal character '%s'" % t.value[0]
			t.lexer.skip(1)
		myLexer = lex.lex()
		myLexer.input(inputFile.read())
		#for token in myLexer:
		#	print token
		# Parser
		from compiler.ast import Printnl, Add, Const, UnarySub, Name, Assign, AssName, CallFunc
		precedence = (
			('nonassoc','PRINT'),
			('left','PLUS')
			)
		def p_print_statement(t):
			'statement : PRINT expression'
			t[0] = Printnl([t[2]], None)
		def p_assign_statement(t):
			'statement : NAME ASSIGN expression'
			t[0] = Assign([AssName(t[1], 'OP_ASSIGN')], t[3])
		def p_plus_expression(t):
			'expression : expression PLUS expression'
			t[0] = Add((t[1], t[3]))
		def p_neg_expression(t):
			'expression : NEG expression'
			t[0] = UnarySub(t[2]) #{'-', '1'}
		def p_int_expression(t):
			'expression : INT'
			t[0] = Const(t[1])
		def p_name_expression(t):
			'expression : NAME'
			t[0] = Name(t[1])
		def p_input_expression(t):
			'expression : INPUT'
			t[0] = CallFunc(Name('input'), [], None, None)
		def p_error(t):
			print "Syntax error at '%s'" % t.value
		parser = yacc.yacc()
		print parser.parse(lexer=myLexer)
		'''
		for token in lexer:
			print token
			result = parser.parse(token)
			print result
			'''
		'''
		#ast = compiler.parse(inputFile.read())
		inputFile.close()
		print ast
		flatAst = flatten(ast)
		printLinkedList(flatAst)
		createAssembly(sys.argv[1][:-2] + "s", flatAst)
		'''
		
		
main()
