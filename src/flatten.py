import compiler
from compiler.ast import *
import structs

	
def newVariable(variables, name):
	if name != None:
		for i in variables:
			if name == variables[i]:
				return i
	ret = structs.Var(len(variables))
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
			if result != None:
				if first == None:	
					first = result
					last = structs.getLast(first)
				else:
					last.next = result
					result.prev = last
					last = structs.getLast(last)
		if last != None:
			last.next = structs.flatNode("FunctionEnd", None, last, None, len(variables), None)
			return structs.flatNode("FunctionStart", first, None, None, len(variables), None)
		return structs.flatNode("FunctionStart", structs.flatNode("FunctionEnd", None, None, None, len(variables), None), None, None, len(variables), None)
	elif isinstance(ast, Printnl):
		result = flattenRecurs(ast.nodes[0], variables)
		if result[0] == None:
			first = structs.flatNode("Print", None, None, None, result[1], None)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("Print", None, last, None, result[1], None)
			last.next = node
		return first
	elif isinstance(ast, Assign):
		result = flattenRecurs(ast.expr, variables)
		output = flattenRecurs(ast.nodes[0], variables)
		if result[0] == None:
			first = structs.flatNode("Assign", None, None, output, result[1], None)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("Assign", None, last, output, result[1], None)
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
			last = structs.getLast(left)
		if right != None:
			if first == None:
				first = right
			else:
				right.prev = last
				last.next = right
			last = structs.getLast(right)
		if first == None:
			first = structs.flatNode("Add", None, None, output, leftTuple[1], rightTuple[1])
		else:
			last.next = structs.flatNode("Add", None, last, output, leftTuple[1], rightTuple[1])
		return (first, output)
		
	elif isinstance(ast, UnarySub):
		result = flattenRecurs(ast.expr, variables)
		output = newVariable(variables, None)
		if result[0] == None:
			first = structs.flatNode("Neg", None, None, output, result[1], None)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("Neg", None, last, output, result[1], None)
			last.next = node
		return first, output
	elif isinstance(ast, CallFunc):
		if ast.node.name == 'input':
			output = newVariable(variables, None)
			return structs.flatNode("Input", None, None, output, None, None), output
			
	else:
		raise Exception("No AST match: " + str(ast))
	
def flatten(ast):
	variables = {}
	return flattenRecurs(ast, variables)

