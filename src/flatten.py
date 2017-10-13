import compiler
from compiler.ast import *
import structs
from src.eStructs import *
	
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
		rightTuple = flattenRecurs(ast.ops[0][1], variables)
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
		if ast.ops[0][0] == "!=":
			instruction = "CompareNE"
		elif ast.ops[0][0] == "==":
			instruction = "CompareEQ"
		elif ast.ops[0][0] == ">=":
			instruction = "CompareGE"
		elif ast.ops[0][0] == ">":
			instruction = "CompareGT"
		elif ast.ops[0][0] == "<=":
			instruction = "CompareLE"
		elif ast.ops[0][0] == "<":
			instruction = "CompareLT"

		if first == None:
			first = structs.flatNode(instruction, None, None, output, leftTuple[1], rightTuple[1])
		else:
			last.next = structs.flatNode(instruction, None, last, output, leftTuple[1], rightTuple[1])
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
		varsList = []
		first = None
		for arg in ast.args:
			result = flattenRecurs(arg, variables)
			varsList.append(result[1])
			if first == None:
				first = result[0]
			else:
				last = structs.getLast(first)
				last.next = result[0]
				result[0].prev = last
		output = newVariable(variables, None)
		funcNode = structs.flatNode("Input", None, None, output, ast.args, None)
		if first == None:
			first = funcNode
		else:
			last = structs.getLast(first)
			last.next = funcNode
			funcNode.prev = last
		return first, output
	elif isinstance(ast, IfExp):
		result0 = flattenRecurs(ast.test, variables)
		result1 = flattenRecurs(ast.then, variables)
		result2 = flattenRecurs(ast.else_, variables)
		first = result0[0]
		last = structs.getLast(first)
		output = newVariable(variables, None)
		ifNode = structs.flatNode("IfExp", None, last, output, result0[1], None)
		first1 = result1[0]
		first2 = result2[0]
		last1 = structs.getLast(first1)
		last2 = structs.getLast(first2)
		if first1 != None:
			last1.next = structs.flatNode("Assign", None, last1, output, result1[1], None)
		else:
			first1 = structs.flatNode("Assign", None, None, output, result1[1], None)
		if first2 != None:
			last2.next = structs.flatNode("Assign", None, last2, output, result2[1], None)
		else:
			first2 = structs.flatNode("Assign", None, None, output, result2[1], None)
		ifNode.thenNext = first1
		first1.prev = ifNode
		ifNode.elseNext = first2
		first2.prev = ifNode
		return first, output
	elif isinstance(ast, GetTag):
		result = flattenRecurs(ast.arg, variables)
		output = newVariable(variables, None)
		print str(ast.arg)
		print str(result)
		if result[0] == None:
			first = structs.flatNode("GetTag", None, None, output, result[1], None)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("GetTag", None, last, output, result[1], None)
			last.next = node
		return first, output
	elif isinstance(ast, ProjectTo):
		result = flattenRecurs(ast.arg, variables)
		output = newVariable(variables, None)
		if result[0] == None:
			first = structs.flatNode("ProjectTo", None, None, output, result[1], ast.typ.value)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("ProjectTo", None, last, output, result[1], ast.typ.value)
			last.next = node
		return first, output	
	elif isinstance(ast, InjectFrom):
		result = flattenRecurs(ast.arg, variables)
		output = newVariable(variables, None)
		if result[0] == None:
			first = structs.flatNode("InjectFrom", None, None, output, result[1], ast.typ.value)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("InjectFrom", None, last, output, result[1], ast.typ.value)
			last.next = node
		return first, output
	elif isinstance(ast, Let):
		output = newVariable(variables, ast.var.name)
		result0 = flattenRecurs(ast.body, variables)
		result1 = flattenRecurs(ast.rhs, variables)
		first1 = result1[0]
		first0 = result0[0]
		last = structs.getLast(first1)
		assignNode = structs.flatNode("Assign", first1, last, output, first1, None)
		if first1 != None:
			last.next = assignNode
		else:
			first1 = assignNode
		if first0 != None:
			first0.prev = assignNode
		return first1, result0[1]
	else:
		raise Exception("No AST match: " + str(ast))
	
def flatten(ast):
	variables = {}
	return (flattenRecurs(ast, variables), variables)

