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
	new_var = str(variables[0])
	variables[len(variables) - 1][name] = new_var
	variables[0] += 1
	return new_var

def uniquifyWrapper(ast):
	variables = [0, {}]
	return uniquify(ast, variables)

def uniquify(ast, variables):
	if isinstance(ast, Module):
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
		return AssName(newVariable(ast.name, variables, True), ast.flags)
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
		return Subscript(uniquify(ast.expr, variables), ast.flag, uniquify(ast.subs[0], variables))
	elif isinstance(ast, IfExp):
		return IfExp(uniquify(ast.test, variables), uniquify(ast.then, variables), uniquify(ast.else_, variables))
	elif isinstance(ast, Return):
		return Return(uniquify(ast.value, variables))
	elif isinstance(ast, Function):
		func_name = newVariable(ast.name, variables, True)
		variables.append({})
		new_argNames = []
		for arg in ast.argnames:
			new_argNames.append(newVariable(arg, variables, True))
		ret = Function(None, func_name, new_argNames, [], 0, None, uniquify(ast.code, variables))
		del variables[-1]
		return ret
	elif isinstance(ast, Lambda):
		variables.append({})
		new_argNames = []
		for arg in ast.argnames:
			new_argNames.append(newVariable(arg, variables, True))
		ret = Lambda(new_argNames, [], 0, uniquify(ast.code, variables))
		del variables[-1]
		return ret
	else:
		raise Exception("No AST match: " + str(ast))