import compiler
from compiler.ast import *
from eStructs import *


INT = 0
BOOL = 1
BIG = 3

'''
Need Let(x, e1, e2), GetTag(x), InjectFrom(TAG,e), and ProjectTo(TAG,e)
'''

def newVariable(variables):
	ret = Name(str(len(variables)))
	variables[ret] = name
	return ret

def ifElseChain(conditions, actions):
	if len(conditions) != (len(actions) - 1):
		raise Exception("conditions don't match actions")
	struct = actions[-1]
	for i in range(0, len(conditions)):
		struct = IfExp(conditions[i], actions[i], struct)
	return struct

def explicate(ast, variables):
	if isinstance(ast, Module):
		return Module(None, explicate(ast.node, variables))
	elif isinstance(ast, Stmt):
		newStmts = []
		for statement in ast.nodes:
			newStmts.append(explicate(statement, variables))
		return Stmt(newStmts)
	elif isinstance(ast, Printnl):
		return CallFunc("print_any", explicate(ast.nodes[0], variables))
	elif isinstance(ast, Assign):
		return Assign(explicate(ast.nodes[0], variables), explicate(ast.expr, variables))
	elif isinstance(ast, AssName):
		return ast
	elif isinstance(ast, Discard):
		return Discard(explicate(ast.expr, variables))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Name):
		return ast
	elif isinstance(ast, Add):
		x = newVariable(variables)
		y = newVariable(variables)
		conditions = []
		actions = []
		conditions.append(Or(And(Compare(GetTag(x), [('==', INT)]), Compare(GetTag(y), [('==', INT)]), And(Compare(GetTag(x), [('==', BOOL)]), Compare(GetTag(y), [('==', BOOL)])))))
		actions.append(InjectFrom(INT, Add(ProjectTo(INT, x),ProjectTo(INT,y))))
		conditions.append(And(Compare(GetTag(x), [('==', BIG)]), Compare(GetTag(y), [('==', BIG)])))
		actions.append(InjectFrom(BIG,CallFunc("add", [ProjectTo(BIG, x), ProjectTo(BIG, y)])))
		actions.append(CallFunc("Abort", []))
		return Let(x, explicate(ast.left, variables), Let(y, explicate(ast.right, variables), ifElseChain(conditions,actions)))
	elif isinstance(ast, Compare):
		x = newVariable(variables)
		y = newVariable(variables)
		conditions = []
		actions = []
		conditions.append(Or(And(Compare(GetTag(x), [('==', INT)]), Compare(GetTag(y), [('==', INT)]), And(Compare(GetTag(x), [('==', BOOL)]), Compare(GetTag(y), [('==', BOOL)])))))
		actions.append(InjectFrom(BOOL, Compare(ProjectTo(INT, x),[(ast.ops[0][0],ProjectTo(INT,y))])))
		conditions.append(And(Compare(GetTag(x), [('==', BIG)]), Compare(GetTag(y), [('==', BIG)])))
		actions.append(InjectFrom(BIG,CallFunc("equal_pyobj", [x, y])))
		actions.append(CallFunc("Abort", []))
		return Let(x, explicate(ast.expr, variables), Let(y, explicate(ast.ops[0][1], variables), ifElseChain(conditions,actions)))
	elif isinstance(ast, And):
		x = newVariable(variables)
		return Let(x, ast.nodes[0], IfExp(ProjectTo(BOOL, x), ast.nodes[1], x))
	elif isinstance(ast, Or):
		x = newVariable(variables)
		return Let(x, ast.nodes[0], IfExp(Not(ProjectTo(BOOL, x)), ast.nodes[1], x))
	elif isinstance(ast, UnarySub):
		x = newVariable(variables)
		conditions = [Or(Eq(GetTag(x), INT), Eq(GetTag(x), BOOL))]
		actions = [InjectFrom(INT, UnarySub(ProjectTo(INT, x))), CallFunc("abort", [])]
		return Let(x, ast.expr, ifElseChain(conditions, actions))
	elif isinstance(ast, Not):
		x = newVariable(variables)
		conditions = [Or(Eq(GetTag(x), INT), Eq(GetTag(x), BOOL))]
		actions = [InjectFrom(BOOL, Not(ProjectTo(BOOL, x))), CallFunc("abort", [])]
		return Let(x, ast.expr, ifElseChain(conditions, actions))
	elif isinstance(ast, CallFunc):
		newArgs = []
		for arg in ast.args:
			newArgs.append(explicate(arg, variables))
		return CallFunc(ast.node, newArgs)
	elif isinstance(ast, List):
		newNodes = []
		for node in ast.nodes:
			newNodes.append(explicate(node, variables))
		return List(newNodes)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((explicate(item[0],variables),explicate(item[1],variables)))
		return ast
	elif isinstance(ast, Subscript):
		return CallFunc("get_subscript", [explicate(ast.expr, variables),explicate(ast.subs[0], variables)])
	elif isinstance(ast, IfExp):
		return IfExp(explicate(ast.test, variables), explicate(ast.then, variables), explicate(ast.else_, variables))
	else:
		raise Exception("No AST match: " + str(ast))


Subscript(Name('dict1'), 'OP_APPLY', [Const(1)])