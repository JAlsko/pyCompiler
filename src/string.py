import compiler
from compiler.ast import *
from eStructs import * 

def newString(string, strings):
	if not string in strings:
		strings[string] = "s" + str(len(strings))
	return strings[string]

def rmString(ast, strings):
	if isinstance(ast, Module):
		return Module(None, rmString(ast.node, strings))
	elif isinstance(ast, Stmt):
		newStmts = []
		for node in ast.nodes:
			newStmts.append(rmString(node, strings))
		return Stmt(newStmts)
	elif isinstance(ast, Assign):
		return Assign(ast.nodes, rmString(ast.expr, strings))
	elif isinstance(ast, Discard):
		return Discard(rmString(ast.expr, strings))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, String):
		label = newString(ast.value, strings)
		return GlobalFuncName(label)
	elif isinstance(ast, Bool):
		return ast
	elif isinstance(ast, Name):
		return ast
	elif isinstance(ast, Add):
		return Add((rmString(ast.left, strings), rmString(ast.right, strings)))
	elif isinstance(ast, Compare):
		return Compare(rmString(ast.expr, strings),[(ast.ops[0][0], rmString(ast.ops[0][1], strings))])
	elif isinstance(ast, UnarySub):
		return UnarySub(rmString(ast.expr, strings))
	elif isinstance(ast, Not):
		return Not(rmString(ast.expr, strings))
	elif isinstance(ast, CallFunc):
		newArgs = []
		for arg in ast.args:
			newArgs.append(rmString(arg, strings))
		return CallFunc(rmString(ast.node, strings), newArgs)
	elif isinstance(ast, IfExp):
		return IfExp(rmString(ast.test, strings), rmString(ast.then, strings), rmString(ast.else_, strings))
	elif isinstance(ast, Let):
		return Let(rmString(ast.var, strings), rmString(ast.rhs, strings), rmString(ast.body, strings))
	elif isinstance(ast, InjectFrom):
		return InjectFrom(ast.typ, rmString(ast.arg, strings))
	elif isinstance(ast, ProjectTo):
		return ProjectTo(ast.typ, rmString(ast.arg, strings))
	elif isinstance(ast, GetTag):
		return GetTag(rmString(ast.arg, strings))
	elif isinstance(ast, Lambda):
		return Lambda(ast.argnames, [], 0, rmString(ast.code, strings))
	elif isinstance(ast, GlobalFuncName):
		return ast
	elif isinstance(ast, Return):
		return Return(rmString(ast.value, strings))
	elif isinstance(ast, List):
		newElem = []
		for elem in ast.nodes:
			newElem.append(rmString(elem, strings))
		return List(newElem)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((rmString(item[0], strings), rmString(item[1], strings)))
		return Dict(newItems)
	elif isinstance(ast, If):
		return If([(rmString(ast.tests[0][0], strings), rmString(ast.tests[0][1], strings))], rmString(ast.else_, strings))
	elif isinstance(ast, While):
		return While(rmString(ast.test, strings), rmString(ast.body, strings), None)
	else:
		raise Exception("No AST match: " + str(ast))