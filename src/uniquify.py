import compiler
from compiler.ast import *

protected_names = ["True", "False", "input"]

def newVariable(name, variables, assignment):
	if name in protected_names:
		return name
	if assignment:
		if name in variables[-1]:
			return variables[-1][name]
	else:
		for i in range(len(variables) - 1, 0, -1):
			if name in variables[i]:
				return variables[i][name]
	new_var = "u" + str(variables[0])
	variables[len(variables) - 1][name] = new_var
	variables[0] += 1
	return new_var

def uniquifyWrapper(ast):
	variables = [0, {}]
	return uniquify(ast, variables)

def uniquifySearch(ast, variables):
	if isinstance(ast, Module):
		uniquifySearch(ast.node, variables)
	elif isinstance(ast, Stmt):
		for statement in ast.nodes:
			uniquifySearch(statement, variables)
	elif isinstance(ast, Printnl):
		uniquifySearch(ast.nodes[0], variables)
	elif isinstance(ast, Assign):
		uniquifySearch(ast.nodes[0], variables)
		uniquifySearch(ast.expr, variables)
	elif isinstance(ast, AssName):
		newVariable(ast.name, variables, True)
	elif isinstance(ast, Discard):
		uniquifySearch(ast.expr, variables)
	elif isinstance(ast, Const):
		pass
	elif isinstance(ast, Name):
		pass
	elif isinstance(ast, Add):
		uniquifySearch(ast.left, variables)
		uniquifySearch(ast.right, variables)
	elif isinstance(ast, Compare):
		uniquifySearch(ast.expr, variables)
		uniquifySearch(ast.ops[0][1], variables)
	elif isinstance(ast, And):
		uniquifySearch(ast.nodes[0], variables)
		uniquifySearch(ast.nodes[1], variables)
	elif isinstance(ast, Or):
		uniquifySearch(ast.nodes[0], variables)
		uniquifySearch(ast.nodes[1], variables)
	elif isinstance(ast, UnarySub):
		uniquifySearch(ast.expr, variables)
	elif isinstance(ast, Not):
		uniquifySearch(ast.expr, variables)
	elif isinstance(ast, CallFunc):
		for arg in ast.args:
			uniquifySearch(arg, variables)
		uniquifySearch(ast.node, variables)
	elif isinstance(ast, List):
		for node in ast.nodes:
			uniquifySearch(node, variables)
	elif isinstance(ast, Dict):
		for item in ast.items:
			uniquifySearch(item[0],variables)
			uniquifySearch(item[1],variables)
	elif isinstance(ast, Subscript):
		uniquifySearch(ast.expr, variables)
		uniquifySearch(ast.subs[0], variables)
	elif isinstance(ast, IfExp):
		uniquifySearch(ast.test, variables)
		uniquifySearch(ast.then, variables)
		uniquifySearch(ast.else_, variables)
	elif isinstance(ast, Return):
		uniquifySearch(ast.value, variables)
	elif isinstance(ast, Function):
		func_name = newVariable(ast.name, variables, True)
	elif isinstance(ast, Lambda):
		pass
	else:
		raise Exception("No AST match: " + str(ast))


def uniquify(ast, variables):
	if isinstance(ast, Module):
		uniquifySearch(ast.node, variables)
		return Module(None, uniquify(ast.node, variables))
	elif isinstance(ast, Stmt):
		newStmts = []
		for statement in ast.nodes:
			newStmts.append(uniquify(statement, variables))
		return Stmt(newStmts)
	elif isinstance(ast, Printnl):
		return Printnl([uniquify(ast.nodes[0], variables)], ast.dest)
	elif isinstance(ast, Assign):
		return Assign([uniquify(ast.nodes[0], variables)], uniquify(ast.expr, variables))
	elif isinstance(ast, AssName):
		return AssName(newVariable(ast.name, variables, False), ast.flags)
	elif isinstance(ast, Discard):
		return Discard(uniquify(ast.expr, variables))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Name):
		return Name(newVariable(ast.name, variables, False))
	elif isinstance(ast, Add):
		return Add((uniquify(ast.left, variables), uniquify(ast.right, variables)))
	elif isinstance(ast, Compare):
		return Compare(uniquify(ast.expr, variables),[(ast.ops[0][0],uniquify(ast.ops[0][1], variables))])
	elif isinstance(ast, And):
		return And([uniquify(ast.nodes[0], variables),uniquify(ast.nodes[1], variables)])
	elif isinstance(ast, Or):
		return Or([uniquify(ast.nodes[0], variables),uniquify(ast.nodes[1], variables)])
	elif isinstance(ast, UnarySub):
		return UnarySub(uniquify(ast.expr, variables))
	elif isinstance(ast, Not):
		return Not(uniquify(ast.expr, variables))
	elif isinstance(ast, CallFunc):
		uniqArgs = []
		for arg in ast.args:
			uniqArgs.append(uniquify(arg, variables))
		return CallFunc(uniquify(ast.node, variables), uniqArgs)
	elif isinstance(ast, List):
		newNodes = []
		for node in ast.nodes:
			newNodes.append(uniquify(node, variables))
		return List(newNodes)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((uniquify(item[0],variables),uniquify(item[1],variables)))
		return Dict(newItems)
	elif isinstance(ast, Subscript):
		return Subscript(uniquify(ast.expr, variables), ast.flags, uniquify(ast.subs[0], variables))
	elif isinstance(ast, IfExp):
		return IfExp(uniquify(ast.test, variables), uniquify(ast.then, variables), uniquify(ast.else_, variables))
	elif isinstance(ast, Return):
		return Return(uniquify(ast.value, variables))
	elif isinstance(ast, Function):
		func_name = newVariable(ast.name, variables, False)
		variables.append({})
		new_argNames = []
		for arg in ast.argnames:
			new_argNames.append(newVariable(arg, variables, True))
		uniquifySearch(ast.code, variables)
		ret = Function(None, func_name, new_argNames, [], 0, None, uniquify(ast.code, variables))
		del variables[-1]
		return ret
	elif isinstance(ast, Lambda):
		variables.append({})
		new_argNames = []
		for arg in ast.argnames:
			new_argNames.append(newVariable(arg, variables, True))
		uniquifySearch(ast.code, variables)
		ret = Lambda(new_argNames, [], 0, uniquify(ast.code, variables))
		del variables[-1]
		return ret
	else:
		raise Exception("No AST match: " + str(ast))