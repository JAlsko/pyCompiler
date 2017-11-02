import compiler
from compiler.ast import *
from eStructs import * 

def closureWrapper(ast):
	functions = {}
	closure(ast, functions)
	return functions

def closure(ast, functions):
	if isinstance(ast, Module):
		main = closure(ast.node, functions)
		functions["main"] = main
		return None
	elif isinstance(ast, Stmt):
		newStmts = []
		for node in ast.nodes:
			newStmts.append(closure(node, functions))
		return Stmt(newStmts)
	elif isinstance(ast, Assign):
		return Assign(ast.nodes, closure(ast.expr, functions))
	elif isinstance(ast, Discard):
		return Discard(closure(ast.expr, functions))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Bool):
		return ast
	elif isinstance(ast, Name):
		return ast
	elif isinstance(ast, Add):
		return Add((closure(ast.left, functions), closure(ast.right, functions)))
	elif isinstance(ast, Compare):
		return Compare(closure(ast.expr, functions),[(ast.ops[0][0], closure(ast.ops[0][1], functions))])
	elif isinstance(ast, UnarySub):
		return UnarySub(closure(ast.expr, functions))
	elif isinstance(ast, Not):
		return Not(closure(ast.expr, functions))
	elif isinstance(ast, CallFunc):
		if isinstance(ast.node, GlobalFuncName):
			newArgs = []
			for arg in ast.args:
				newArgs.append(closure(arg, functions))
			return CallFunc(ast.node, newArgs)
		else:
			ret = closure(ast.node)
			newArgs = [CallFunc(GlobalFuncName('get_free_vars'), ret)]
			for arg in ast.args:
				newArgs.append(closure(arg, functions))
			return CallFunc(CallFunc(), newArgs)
	elif isinstance(ast, IfExp):
		return IfExp(closure(ast.test, functions), closure(ast.then, functions), closure(ast.else_, functions))
	elif isinstance(ast, Let):
		return Let(closure(ast.var, functions), closure(ast.rhs, functions), closure(ast.body, functions))
	elif isinstance(ast, InjectFrom):
		return InjectFrom(ast.typ, closure(ast.arg, functions))
	elif isinstance(ast, ProjectTo):
		return ProjectTo(ast.typ, closure(ast.arg, functions))
	elif isinstance(ast, GetTag):
		return GetTag(closure(ast.arg, functions))
	elif isinstance(ast, Lambda):
		pass
	elif isinstance(ast, RuntimeFunc):
		return ast
	elif isinstance(ast, Return):
		return Return(closure(ast.value, functions))
	else:
		raise Exception("No AST match: " + str(ast))