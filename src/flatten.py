import compiler
from compiler.ast import *
import structs
from src.eStructs import *
	
def newVariable(variables, name):
	if name != None:
		for i in variables:
			if name == variables[i]:
				return i
	ret = structs.Var("t" + str(len(variables)))
	variables[ret] = name
	return ret

def flattenRecurs(ast, variables):
	#print str(ast)
	#print ""
	if isinstance(ast, Lambda):
		new_args = []
		for var in ast.argnames:
			new_args.append(newVariable(variables, var))
		first = flattenRecurs(ast.code, variables)
		last = structs.getLast(first)
		if last != None:
			last.next = structs.flatNode("FunctionEnd", None, last, None, None, None)
			return structs.flatNode("FunctionStart", first, None, new_args, None, None)
		return structs.flatNode("FunctionStart", structs.flatNode("FunctionEnd", None, None, None, None, None), None, new_args, None, None)
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
					if isinstance(result, tuple):
						print str(result[0])
					last.next = result
					result.prev = last
					last = structs.getLast(last)
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
	elif isinstance(ast, Bool):
		return None, ast.value
	elif isinstance(ast, Name):
		return None, newVariable(variables, ast.name)
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

	elif isinstance(ast, Return):
		result = flattenRecurs(ast.value, variables)
		output = newVariable(variables, None)
		if result[0] == None:
			first = structs.flatNode("Return", None, None, None, result[1], None)
		else:
			first = result[0]
			last = structs.getLast(first)
			node = structs.flatNode("Return", None, last, None, result[1], None)
			last.next = node
		return first

	elif isinstance(ast, CallFunc):
		varsList = []
		first = None
		result = flattenRecurs(ast.node, variables)
		func = result[1]
		if result[0] != None:
			if first == None:
				first = result[0]
		for arg in ast.args:
			result = flattenRecurs(arg, variables)
			varsList.append(result[1])
			if result[0] != None:
				if first == None:
					first = result[0]
				else:
					last = structs.getLast(first)
					last.next = result[0]
					result[0].prev = last
		output = newVariable(variables, None)
		funcNode = structs.flatNode("CallFunc", None, None, output, func, varsList)
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
		if first == None:
			first = ifNode
		else:
			last.next = ifNode
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
		#print str(ast)
		#structs.printLLwithIf(first, 0)
		return first, output
	elif isinstance(ast, If):
		result0 = flattenRecurs(ast.tests[0][0], variables)
		result1 = flattenRecurs(ast.tests[0][1], variables)
		result2 = flattenRecurs(ast.else_, variables)
		first = result0[0]
		last = structs.getLast(first)
		ifNode = structs.flatNode("IfExp", None, last, None, result0[1], None)
		if first == None:
			first = ifNode
		else:
			last.next = ifNode
		ifNode.thenNext = result1
		result1.prev = ifNode
		ifNode.elseNext = result2
		result2.prev = ifNode
		return first
	elif isinstance(ast, While):
		result0 = flattenRecurs(ast.test, variables)
		result1 = flattenRecurs(ast.body, variables)
		first = result0[0]
		last = structs.getLast(first)
		whileNode = structs.flatNode("While", None, last, None, result0[1], None)
		if first == None:
			first = whileNode
		else:
			last.next = whileNode
		whileNode.thenNext = result1
		result1.prev = whileNode
		return first
	elif isinstance(ast, GetTag):
		result = flattenRecurs(ast.arg, variables)
		output = newVariable(variables, None)
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
		result1 = flattenRecurs(ast.body, variables)
		result0 = flattenRecurs(ast.rhs, variables)
		first0 = result0[0]
		first1 = result1[0]
		last = structs.getLast(first0)
		assignNode = structs.flatNode("Assign", first1, last, output, result0[1], None)
		if first0 != None:
			last.next = assignNode
		else:
			first0 = assignNode
		if first1 != None:
			first1.prev = assignNode
		return first0, result1[1]
	elif isinstance(ast, List):
		first = None
		listElem = []
		for node in ast.nodes:
			result = flattenRecurs(node, variables)
			listElem.append(result[1])
			if result[0] != None:
				if first == None:
					first = result[0]
				else:
					last = structs.getLast(first)
					last.next = result[0]
					result[0].prev = last
		output = newVariable(variables, None)
		tmp = newVariable(variables, None)
		tmp2 = newVariable(variables, None)
		injectNode = structs.flatNode("InjectFrom", None, None, tmp, len(ast.nodes), 0)
		listNode = structs.flatNode("CallFunc", None, injectNode, tmp2, GlobalFuncName("create_list"), [tmp])
		injectNode2 = structs.flatNode("InjectFrom", None, listNode, output, tmp2, 3)
		injectNode.next = listNode
		listNode.next = injectNode2
		if first == None:
			first = injectNode
		else:
			last = structs.getLast(first)
			last.next = injectNode
			injectNode.prev = last
		last = injectNode2
		for i in range(0, len(listElem)):
			tmp = newVariable(variables, None)
			last.next = structs.flatNode("InjectFrom", None, last, tmp, i, 0)
			last = last.next
			last.next = structs.flatNode("CallFunc", None, last, None, GlobalFuncName("set_subscript"), [output, tmp, listElem[i]])
			last = last.next
		return first, output
	elif isinstance(ast, Dict):
		first = None
		dictElem = {}
		for item in ast.items:

			result = flattenRecurs(item[1], variables)
			elem = result[1]
			if first == None:
				first = result[0]
			else:
				last = structs.getLast(first)
				last.next = result[0]
				result[0].prev = last

			result = flattenRecurs(item[0], variables)
			dictElem[result[1]] = elem
			if first == None:
				first = result[0]
			else:
				last = structs.getLast(first)
				last.next = result[0]
				result[0].prev = last
		output = newVariable(variables, None)
		tmp = newVariable(variables, None)
		dictNode = structs.flatNode("CallFunc", None, None, tmp, GlobalFuncName("create_dict"), [])
		injectNode = structs.flatNode("InjectFrom", None, dictNode, output, tmp, 3)
		dictNode.next = injectNode
		if first == None:
			first = dictNode
		else:
			last = structs.getLast(first)
			last.next = dictNode
			dictNode.prev = last
		last = injectNode
		for key in dictElem:
			last.next = structs.flatNode("CallFunc", None, last, None, GlobalFuncName("set_subscript"), [output, key, dictElem[key]])
			last = last.next
		return first, output
	elif isinstance(ast, GlobalFuncName):
		return None, ast
	else:
		raise Exception("No AST match: " + str(ast))

def flatten(ast):
	variables = {}
	return (flattenRecurs(ast, variables), variables)

