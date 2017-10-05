import compiler
from compiler.ast import *
from eStructs import *

variables = {}

INT = 0
BOOL = 1
BIG = 3

'''
Need Let(x, e1, e2), GetTag(x), InjectFrom(TAG,e), and ProjectTo(TAG,e)
'''

def newVariable(variables, name):
	if name != None:
		for i in variables:
			if name == variables[i]:
				return i
	ret = Name(str(len(variables)))
	variables[ret] = name
	return ret

def ifElseChain(conditions, actions):
	if len(conditions) != (len(actions) - 1):
		raise Exception("conditions don't match actions")
	struct = actions[-1]
	for i in range(0, len(conditions)):
		struct = IfExpr(conditions[i], actions[i], struct)
	return struct

def explicate(ast, variables):
	if isinstance(ast, Assign):
		x = newVariable(variables)
		y = newVariable(variables)
		conditions = [And(Eq(GetTag(x), INT), Eq(GetTag(y), INT)), And(Eq(GetTag(x), BOOL), Eq(GetTag(y), BOOL)), And(Eq(GetTag(x), BIG), Eq(GetTag(y), BIG))]
		actions = [AddInt(x,y), AddBool(x,y), AddBig(x,y), CallFunc("Abort")]
		working = Let(x, explicate(ast.left, variables), Let(y, explicate(ast.right, variables), ifElseChain(conditions,actions)))
		return working

	if isinstance(ast, Add):
		x = newVariable(variables)
		y = newVariable(variables)
		conditions = [And(Eq(GetTag(x), INT), Eq(GetTag(y), INT)), And(Eq(GetTag(x), BOOL), Eq(GetTag(y), BOOL)), And(Eq(GetTag(x), BIG), Eq(GetTag(y), BIG))]
		actions = [AddInt(x,y), AddBool(x,y), AddBig(x,y), CallFunc("Abort")]
		working = Let(x, explicate(ast.left, variables), Let(y, explicate(ast.right, variables), ifElseChain(conditions,actions)))
		return working