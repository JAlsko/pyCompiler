import compiler
from compiler.ast import *
import structs
	
def newVariable(variables, name):
	if name != None:
		for i in variables:
			if name == variables[i]:
				return i
	ret = structs.Var(str(len(variables)))
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

	elif isinstance(ast, Compare):
		leftTuple = flattenRecurs(ast.expr, variables)
		left = leftTuple[0]
		rightTuple = flattenRecurs(ast.ops[1], variables)
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

		instruction = "Compare"
		if ast.ops[0] == "!=":
			instruction = "CompareNE"
		elif ast.ops[0] == "==":
			instruction = "CompareEQ"
		elif ast.ops[0] == ">=":
			instruction = "CompareGE"
		elif ast.ops[0] == ">":
			instruction = "CompareGT"
		elif ast.ops[0] == "<=":
			instruction = "CompareLE"
		elif ast.ops[0] == "<":
			instruction = "CompareLT"

		if first == None:
			first = structs.flatNode(instruction, None, None, output, leftTuple[1], rightTuple[1])
		else:
			last.next = structs.flatNode(instruction, None, last, output, leftTuple[1], rightTuple[1])
		return (first, output)
	
	elif isinstance(ast, And):
		leftTuple = flattenRecurs(ast.nodes[0], variables)
		left = leftTuple[0]
		rightTuple = flattenRecurs(ast.nodes[1], variables)
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
			first = structs.flatNode("And", None, None, output, leftTuple[1], rightTuple[1])
		else:
			last.next = structs.flatNode("And", None, last, output, leftTuple[1], rightTuple[1])
		return (first, output)

	elif isinstance(ast, Or):
		leftTuple = flattenRecurs(ast.nodes[0], variables)
		left = leftTuple[0]
		rightTuple = flattenRecurs(ast.nodes[1], variables)
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
			first = structs.flatNode("Or", None, None, output, leftTuple[1], rightTuple[1])
		else:
			last.next = structs.flatNode("Or", None, last, output, leftTuple[1], rightTuple[1])
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

	elif isinstance(ast, Not):
		result = flattenRecurs(ast.expr, variables)
		output = newVariable(variables, None)
		if result[0] == None:
			first = structs.flatNode("Not", None, None, output, result[1], None)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("Not", None, last, output, result[1], None)
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
	return (flattenRecurs(ast, variables), variables)

