import compiler
from compiler.ast import *
from eStructs import *


INT = 0
BOOL = 1
BIG = 3

'''
Screenshot from 2017-10-12 11-11-04Need Let(x, e1, e2), GetTag(x), InjectFrom(TAG,e), and ProjectTo(TAG,e)
'''

def newVariable(variables):
	ret = Name( "e" + str(len(variables)))
	variables.append(ret)
	return ret

def ifElseChain(conditions, actions):
	if len(conditions) != (len(actions) - 1):
		raise Exception("conditions don't match actions")
	struct = actions[-1]
	for i in range(0, len(conditions)):
		struct = IfExp(conditions[i], actions[i], struct)
	return struct

def qAnd(e1,e2, variables):
	x = newVariable(variables)
	return Let(x, e1, IfExp( x, e2, x))

def qOr(e1,e2, variables):
	x = newVariable(variables)
	return Let(x, e1, IfExp(Not(x), e2, x))

def getBool(e1, variables):
	conditions = []
	actions = []
	conditions.append(qOr(Compare(GetTag(e1), [("==", Const(INT))] ), Compare(GetTag(e1), [("==", Const(BOOL))] ), variables))
	actions.append(ProjectTo(Const(BOOL), e1))
	conditions.append(Compare(GetTag(e1), [("==", Const(BIG))] ))
	actions.append(Not(qOr(CallFunc(GlobalFuncName("equal"), [ProjectTo(Const(BIG), e1), ProjectTo(Const(BIG), List([]))]),CallFunc(GlobalFuncName("equal"), [ProjectTo(Const(BIG), e1), ProjectTo(Const(BIG), Dict([]))]), variables)))
	actions.append(CallFunc(GlobalFuncName("abort"), []))
	return ifElseChain(conditions, actions)

def explicate(ast, variables):
	if isinstance(ast, Module):
		ret = Module(None, explicate(ast.node, variables))
		return ret
	elif isinstance(ast, Stmt):
		newStmts = []
		for statement in ast.nodes:
			newStmts.append(explicate(statement, variables))
		return Stmt(newStmts)
	elif isinstance(ast, Printnl):
		return Discard(CallFunc(GlobalFuncName("print_any"), [explicate(ast.nodes[0], variables)]))
	elif isinstance(ast, Assign):
		if isinstance(ast.nodes[0], Subscript):
			return Discard(CallFunc(GlobalFuncName("set_subscript"), [explicate(ast.nodes[0].expr, variables), explicate(ast.nodes[0].subs[0], variables), explicate(ast.expr, variables)]))
		else:
			return Assign([explicate(ast.nodes[0], variables)], explicate(ast.expr, variables))
	elif isinstance(ast, AssName):
		return ast
	elif isinstance(ast, Discard):
		return Discard(explicate(ast.expr, variables))
	elif isinstance(ast, Const):
		return InjectFrom(Const(INT), ast)
	elif isinstance(ast, Name):
		if ast.name == "True":
			return InjectFrom(Const(BOOL),Bool(True))
		elif ast.name == "False":
			return InjectFrom(Const(BOOL),Bool(False))
		else:
			return ast
	elif isinstance(ast, Add):
		x = newVariable(variables)
		y = newVariable(variables)
		conditions = []
		actions = []
		conditions.append(qOr(qAnd(Compare(GetTag(x), [('==', Const(INT))]), Compare(GetTag(y), [('==', Const(INT))]), variables),qAnd(Compare(GetTag(x), [('==', Const(BOOL))]), Compare(GetTag(y), [('==', Const(BOOL))]), variables), variables))
		actions.append(InjectFrom(Const(INT), Add((ProjectTo(Const(INT), x),ProjectTo(Const(INT),y)))))
		conditions.append(qAnd(Compare(GetTag(x), [('==', Const(BIG))]), Compare(GetTag(y), [('==', Const(BIG))]), variables))
		actions.append(InjectFrom(Const(BIG),CallFunc(GlobalFuncName("add"), [ProjectTo(Const(BIG), x), ProjectTo(Const(BIG), y)])))
		actions.append(CallFunc(GlobalFuncName("abort"), []))
		return Let(x, explicate(ast.left, variables), Let(y, explicate(ast.right, variables), ifElseChain(conditions,actions)))
	elif isinstance(ast, Compare):
		if ast.ops[0][0] != "is":
			x = newVariable(variables)
			y = newVariable(variables)
			conditions = []
			actions = []
			conditions.append(qOr(qAnd(Compare(GetTag(x), [('==', Const(INT))]), Compare(GetTag(y), [('==', Const(INT))]), variables),qAnd(Compare(GetTag(x), [('==', Const(BOOL))]), Compare(GetTag(y), [('==', Const(BOOL))]), variables), variables))
			actions.append(InjectFrom(Const(BOOL), Compare(ProjectTo(Const(INT), x),[(ast.ops[0][0],ProjectTo(Const(INT),y))])))
			conditions.append(qAnd(Compare(GetTag(x), [('==', Const(BIG))]), Compare(GetTag(y), [('==', Const(BIG))]), variables))
			actions.append(InjectFrom(Const(BOOL),CallFunc(GlobalFuncName("equal"), [ProjectTo(Const(BIG), x), ProjectTo(Const(BIG), y)])))
			actions.append(CallFunc(GlobalFuncName("abort"), []))
			return Let(x, explicate(ast.expr, variables), Let(y, explicate(ast.ops[0][1], variables), ifElseChain(conditions,actions)))
		else:
			return InjectFrom(Const(BOOL), Compare(explicate(ast.expr, variables), [("==", explicate(ast.ops[0][1], variables))]))
	elif isinstance(ast, And):
		x = newVariable(variables)
		return Let(x, explicate(ast.nodes[0], variables), IfExp(getBool(x, variables), explicate(ast.nodes[1], variables), x))
	elif isinstance(ast, Or):
		x = newVariable(variables)
		return Let(x, explicate(ast.nodes[0], variables), IfExp(Not(getBool(x, variables)), explicate(ast.nodes[1], variables), x))
	elif isinstance(ast, UnarySub):
		x = newVariable(variables)
		conditions = [qOr(Compare(GetTag(x), [("==", Const(INT))] ), Compare(GetTag(x), [("==", Const(BOOL))] ), variables)]
		actions = [InjectFrom(Const(INT), UnarySub(ProjectTo(Const(INT), x))), CallFunc(GlobalFuncName("abort"), [])]
		return Let(x, explicate(ast.expr, variables), ifElseChain(conditions, actions))
	elif isinstance(ast, Not):
		x = newVariable(variables)
		return Let(x, explicate(ast.expr, variables), InjectFrom(Const(BOOL), Not(getBool(x, variables))))
	elif isinstance(ast, CallFunc):
		newArgs = []
		for arg in ast.args:
			newArgs.append(explicate(arg, variables))
		return InjectFrom(Const(INT), CallFunc(explicate(ast.node, variables), newArgs))
	elif isinstance(ast, List):
		newNodes = []
		for node in ast.nodes:
			newNodes.append(explicate(node, variables))
		return List(newNodes)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((explicate(item[0],variables),explicate(item[1],variables)))
		return Dict(newItems)
	elif isinstance(ast, Subscript):
		if ast.flags == 'OP_APPLY':
			return CallFunc(GlobalFuncName("get_subscript"), [explicate(ast.expr, variables),explicate(ast.subs[0], variables)])
	elif isinstance(ast, IfExp):
		x = newVariable(variables)
		return IfExp(Let(x, explicate(ast.test, variables), getBool(x, variables)), explicate(ast.then, variables), explicate(ast.else_, variables))
	elif isinstance(ast, Return):
		return Return(explicate(ast.value, variables))
	elif isinstance(ast, Lambda):
		return Lambda(ast.argnames, ast.defaults, ast.flags, Stmt([Return(explicate(ast.code, variables))]))
	elif isinstance(ast, Function):
		return Assign([AssName(ast.name, 'OP_ASSIGN')],Lambda(ast.argnames, ast.defaults, ast.flags, explicate(ast.code, variables)))
	else:
		raise Exception("No AST match: " + str(ast))

