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
		return free_vars(ast.expr, variables)
	elif isinstance(ast, Discard):
		return free_vars(ast.expr, variables)
	elif isinstance(ast, Const):
		return set([])
	elif isinstance(ast, Bool):
		return set([])
	elif isinstance(ast, Name):
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
		for thing in ast:
			ret = ret | free_vars(thing, variables)
	elif isinstance(ast, Dict):
		ret = set([])
		for item in ast.items:
			ret = ret | free_vars(item[0], variables) | free_vars(item[1], variables)
		return ret
	elif isinstance(ast, IfExp):
		return free_vars(ast.test, variables) | free_vars(ast.then, variables) | determineHeapify(ast.else_)
	elif isinstance(ast, Let):
		return free_vars(ast.rhs, variables) | free_vars(ast.body, variables)
	elif isinstance(ast, InjectFrom):
		return free_vars(ast.arg, variables)
	elif isinstance(ast, ProjectTo):
		return free_vars(ast.arg, variables)
	elif isinstance(ast, GetTag):
		return free_vars(ast.arg, variables)
	elif isinstance(ast, Lambda):
		return free_vars(ast.code, variables) | (free_vars(ast.code, []) - set(ast.argnames))
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
		for thing in ast:
			ret = ret | determineHeapify(thing)
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
		return determineHeapify(ast.code) | (free_vars(ast.code, []) - set(ast.argnames))
	else:
		raise Exception("No AST match: " + str(ast))

