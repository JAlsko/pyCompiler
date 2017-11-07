import compiler
from compiler.ast import *
from eStructs import * 

def free_vars(ast, variables):
	if isinstance(ast, Module):
		return free_vars(ast.node, variables)
	elif isinstance(ast, Stmt):
		ret = set([])
		for node in ast.nodes:
			ret = ret | free_vars(node, variables)
		return ret
	elif isinstance(ast, Assign):
		return free_vars(ast.expr, variables) | free_vars(ast.nodes[0], variables)
	elif isinstance(ast, AssName):
		variables.add(ast.name)
		return set([])
	elif isinstance(ast, Discard):
		return free_vars(ast.expr, variables)
	elif isinstance(ast, Const):
		return set([])
	elif isinstance(ast, Bool):
		return set([])
	elif isinstance(ast, Name):
		if not ast.name in variables:
			return set([ast.name])
		else:
			return set([])
	elif isinstance(ast, Add):
		return free_vars(ast.left, variables) | free_vars(ast.right, variables)
	elif isinstance(ast, Compare):
		return free_vars(ast.expr, variables) | free_vars(ast.ops[0][1], variables)
	elif isinstance(ast, UnarySub):
		return free_vars(ast.expr, variables)
	elif isinstance(ast, Not):
		return free_vars(ast.expr, variables)
	elif isinstance(ast, CallFunc):
		ret = free_vars(ast.node, variables)
		for arg in ast.args:
			ret = ret | free_vars(arg, variables)
		return ret
	elif isinstance(ast, List):
		ret = set([])
		for thing in ast.nodes:
			ret = ret | free_vars(thing, variables)
		return ret
	elif isinstance(ast, Dict):
		ret = set([])
		for item in ast.items:
			ret = ret | free_vars(item[0], variables) | free_vars(item[1], variables)
		return ret
	elif isinstance(ast, IfExp):
		return free_vars(ast.test, variables) | free_vars(ast.then, variables) | free_vars(ast.else_, variables)
	elif isinstance(ast, Let):
		variables.add(ast.var.name)
		return free_vars(ast.rhs, variables) | free_vars(ast.body, variables)
	elif isinstance(ast, InjectFrom):
		return free_vars(ast.arg, variables)
	elif isinstance(ast, ProjectTo):
		return free_vars(ast.arg, variables)
	elif isinstance(ast, GetTag):
		return free_vars(ast.arg, variables)
	elif isinstance(ast, Lambda):
		return set([])
	elif isinstance(ast, GlobalFuncName):
		return set([])
	elif isinstance(ast, Return):
		return free_vars(ast.value, variables)
	else:
		raise Exception("No AST match: " + str(ast))

def determineHeapify(ast):
	if isinstance(ast, Module):
		return determineHeapify(ast.node)
	elif isinstance(ast, Stmt):
		ret = set([])
		for node in ast.nodes:
			ret = ret | determineHeapify(node)
		return ret
	elif isinstance(ast, Assign):
		return determineHeapify(ast.expr)
	elif isinstance(ast, Discard):
		return determineHeapify(ast.expr)
	elif isinstance(ast, Const):
		return set([])
	elif isinstance(ast, Bool):
		return set([])
	elif isinstance(ast, Name):
		return set([])
	elif isinstance(ast, Add):
		return determineHeapify(ast.left) | determineHeapify(ast.right)
	elif isinstance(ast, Compare):
		return determineHeapify(ast.expr) | determineHeapify(ast.ops[0][1])
	elif isinstance(ast, UnarySub):
		return determineHeapify(ast.expr)
	elif isinstance(ast, Not):
		return determineHeapify(ast.expr)
	elif isinstance(ast, CallFunc):
		ret = determineHeapify(ast.node)
		for arg in ast.args:
			ret = ret | determineHeapify(arg)
		return ret
	elif isinstance(ast, List):
		ret = set([])
		for thing in ast.nodes:
			ret = ret | determineHeapify(thing)
		return ret
	elif isinstance(ast, Dict):
		ret = set([])
		for item in ast.items:
			ret = ret | determineHeapify(item[0]) | determineHeapify(item[1])
		return ret
	elif isinstance(ast, IfExp):
		return determineHeapify(ast.test) | determineHeapify(ast.then) | determineHeapify(ast.else_)
	elif isinstance(ast, Let):
		return determineHeapify(ast.rhs) | determineHeapify(ast.body)
	elif isinstance(ast, InjectFrom):
		return determineHeapify(ast.arg)
	elif isinstance(ast, ProjectTo):
		return determineHeapify(ast.arg)
	elif isinstance(ast, GetTag):
		return determineHeapify(ast.arg)
	elif isinstance(ast, Lambda):
		return determineHeapify(ast.code) | (free_vars(ast.code, set([])) - set(ast.argnames))
	elif isinstance(ast, GlobalFuncName):
		return set([])
	elif isinstance(ast, Return):
		return determineHeapify(ast.value)
	else:
		raise Exception("No AST match: " + str(ast))


def local_vars(ast, variables):
	if isinstance(ast, Module):
		return local_vars(ast.node, variables)
	elif isinstance(ast, Stmt):
		ret = set([])
		for node in ast.nodes:
			ret = ret | local_vars(node, variables)
		return ret
	elif isinstance(ast, Assign):
		return local_vars(ast.expr, variables) | local_vars(ast.nodes[0], variables)
	elif isinstance(ast, AssName):
		if ast.name in variables:
			return set([ast.name])
		else:
			return set([])
	elif isinstance(ast, Discard):
		return local_vars(ast.expr, variables)
	elif isinstance(ast, Const):
		return set([])
	elif isinstance(ast, Bool):
		return set([])
	elif isinstance(ast, Name):
		return set([])
	elif isinstance(ast, Add):
		return local_vars(ast.left, variables) | local_vars(ast.right, variables)
	elif isinstance(ast, Compare):
		return local_vars(ast.expr, variables) | local_vars(ast.ops[0][1], variables)
	elif isinstance(ast, UnarySub):
		return local_vars(ast.expr, variables)
	elif isinstance(ast, Not):
		return local_vars(ast.expr, variables)
	elif isinstance(ast, CallFunc):
		ret = local_vars(ast.node, variables)
		for arg in ast.args:
			ret = ret | local_vars(arg, variables)
		return ret
	elif isinstance(ast, List):
		ret = set([])
		for thing in ast.nodes:
			ret = ret | local_vars(thing, variables)
		return ret
	elif isinstance(ast, Dict):
		ret = set([])
		for item in ast.items:
			ret = ret | local_vars(item[0], variables) | local_vars(item[1], variables)
		return ret
	elif isinstance(ast, IfExp):
		return local_vars(ast.test, variables) | local_vars(ast.then, variables) | determineHeapify(ast.else_)
	elif isinstance(ast, Let):
		return local_vars(ast.rhs, variables) | local_vars(ast.body, variables)
	elif isinstance(ast, InjectFrom):
		return local_vars(ast.arg, variables)
	elif isinstance(ast, ProjectTo):
		return local_vars(ast.arg, variables)
	elif isinstance(ast, GetTag):
		return local_vars(ast.arg, variables)
	elif isinstance(ast, Lambda):
		return set([])
	elif isinstance(ast, GlobalFuncName):
		return set([])
	elif isinstance(ast, Return):
		return local_vars(ast.value, variables)
	else:
		raise Exception("No AST match: " + str(ast))

def heapify(ast, variables):
	if isinstance(ast, Module):
		localVars = local_vars(ast.node, variables)
		newStmts = []
		for var in localVars:
			newStmts.append(Assign([AssName(var, 'OP_ASSIGN')], List([Const(0)])))
		oldStmts = heapify(ast.node, variables)
		for stmt in oldStmts.nodes:
			newStmts.append(stmt) 
		return Module(ast.doc, Stmt(newStmts))
	elif isinstance(ast, Stmt):
		newStmts = []
		for node in ast.nodes:
			newStmts.append(heapify(node, variables))
		return Stmt(newStmts)
	elif isinstance(ast, Assign):
		if ast.nodes[0].name in variables:
			return Discard(CallFunc(GlobalFuncName("set_subscript"), [Name(ast.nodes[0].name), Const(0), heapify(ast.expr, variables)]))
		else:
			return Assign(ast.nodes, heapify(ast.expr, variables))
	elif isinstance(ast, Discard):
		return Discard(heapify(ast.expr, variables))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Bool):
		return ast
	elif isinstance(ast, Name):
		if ast.name in variables:
			return CallFunc(GlobalFuncName("get_subscript"),[ast, Const(0)])
		else:
			return ast
	elif isinstance(ast, Add):
		return Add((heapify(ast.left, variables), heapify(ast.right, variables)))
	elif isinstance(ast, Compare):
		return Compare(heapify(ast.expr, variables),[(ast.ops[0][0], heapify(ast.ops[0][1], variables))])
	elif isinstance(ast, UnarySub):
		return UnarySub(heapify(ast.expr, variables))
	elif isinstance(ast, Not):
		return Not(heapify(ast.expr, variables))
	elif isinstance(ast, CallFunc):
		newArgs = []
		for arg in ast.args:
			newArgs.append(heapify(arg, variables))
		return CallFunc(heapify(ast.node, variables), newArgs)
	elif isinstance(ast, List):
		newElem = []
		for elem in ast.nodes:
			newElem.append(heapify(elem, variables))
		return List(newElem)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((heapify(item[0], variables), heapify(item[1], variables)))
		return Dict(newItems)
	elif isinstance(ast, IfExp):
		return IfExp(heapify(ast.test, variables), heapify(ast.then, variables), heapify(ast.else_, variables))
	elif isinstance(ast, Let):
		return Let(heapify(ast.var, variables), heapify(ast.rhs, variables), heapify(ast.body, variables))
	elif isinstance(ast, InjectFrom):
		return InjectFrom(ast.typ, heapify(ast.arg, variables))
	elif isinstance(ast, ProjectTo):
		return ProjectTo(ast.typ, heapify(ast.arg, variables))
	elif isinstance(ast, GetTag):
		return GetTag(heapify(ast.arg, variables))
	elif isinstance(ast, Lambda):
		newargnames = []
		newStmts = []
		for arg in ast.argnames:
			if arg in variables:
				newargnames.append(arg + "h")
				newStmts.append(Assign([AssName(arg, 'OP_ASSIGN')], List([Const(0)])))
				newStmts.append(Discard(CallFunc(GlobalFuncName("set_subscript"), [Name(arg), Const(0), Name(arg + "h")])))
			else:
				newargnames.append(arg)
		localVars = local_vars(ast.code, variables)
		for var in localVars:
			newStmts.append(Assign([AssName(var, 'OP_ASSIGN')], List([Const(0)])))
		oldStmts = heapify(ast.code, variables)
		for stmt in oldStmts.nodes:
			newStmts.append(stmt)
		return Lambda(newargnames, ast.defaults, ast.flags, Stmt(newStmts))
	elif isinstance(ast, GlobalFuncName):
		return ast
	elif isinstance(ast, Return):
		return Return(heapify(ast.value, variables))
	else:
		raise Exception("No AST match: " + str(ast))

