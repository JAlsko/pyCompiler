import compiler
from compiler.ast import *
from eStructs import * 
from heapify import free_vars

def newVariables(variables):
	ret = variables[0]
	variables[0] += 1
	return Name("l" + str(ret))

def newFunction(functions):
	return "f" + str(len(functions))

def closureWrapper(ast):
	functions = {}
	variables = [0]
	closure(ast, functions, variables)
	return functions

def closure(ast, functions, variables):
	if isinstance(ast, Module):
		main = Lambda([], [], 0, closure(ast.node, functions, variables))
		functions["main"] = main
		return None
	elif isinstance(ast, Stmt):
		newStmts = []
		for node in ast.nodes:
			newStmts.append(closure(node, functions, variables))
		return Stmt(newStmts)
	elif isinstance(ast, Assign):
		return Assign(ast.nodes, closure(ast.expr, functions, variables))
	elif isinstance(ast, Discard):
		return Discard(closure(ast.expr, functions, variables))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Bool):
		return ast
	elif isinstance(ast, Name):
		return ast
	elif isinstance(ast, Add):
		return Add((closure(ast.left, functions, variables), closure(ast.right, functions, variables)))
	elif isinstance(ast, Compare):
		return Compare(closure(ast.expr, functions, variables),[(ast.ops[0][0], closure(ast.ops[0][1], functions, variables))])
	elif isinstance(ast, UnarySub):
		return UnarySub(closure(ast.expr, functions, variables))
	elif isinstance(ast, Not):
		return Not(closure(ast.expr, functions, variables))
	elif isinstance(ast, CallFunc):
		if isinstance(ast.node, GlobalFuncName):
			newArgs = []
			for arg in ast.args:
				newArgs.append(closure(arg, functions, variables))
			return CallFunc(ast.node, newArgs)
		else:
			new_var = newVariables(variables)
			newArgs = [CallFunc(GlobalFuncName('get_free_vars'), [new_var])]
			for arg in ast.args:
				newArgs.append(closure(arg, functions, variables))
			return Let(new_var, closure(ast.node, functions, variables), CallFunc(CallFunc(GlobalFuncName('get_fun_ptr'), [new_var]), newArgs))
	elif isinstance(ast, IfExp):
		return IfExp(closure(ast.test, functions, variables), closure(ast.then, functions, variables), closure(ast.else_, functions, variables))
	elif isinstance(ast, Let):
		return Let(closure(ast.var, functions, variables), closure(ast.rhs, functions, variables), closure(ast.body, functions, variables))
	elif isinstance(ast, InjectFrom):
		return InjectFrom(ast.typ, closure(ast.arg, functions, variables))
	elif isinstance(ast, ProjectTo):
		return ProjectTo(ast.typ, closure(ast.arg, functions, variables))
	elif isinstance(ast, GetTag):
		return GetTag(closure(ast.arg, functions, variables))
	elif isinstance(ast, Lambda):
		new_code = closure(ast.code, functions, variables)
		freeVars = free_vars(new_code, set([])) - set(ast.argnames)
		newStmts = []
		new_var = newVariables(variables)
		i = 0
		for var in freeVars:
			newStmts.append(Assign([AssName(var, 'OP_ASSIGN')], CallFunc(GlobalFuncName('get_subscript'),[new_var, Const(i)])))
			i += 1
		for stmt in new_code.nodes:
			newStmts.append(stmt)
		newargs = [new_var.name] + ast.argnames
		func_name = newFunction(functions)
		functions[func_name] = Lambda(newargs, ast.defaults, ast.flags, Stmt(newStmts))
		free_var_names = []
		for var in freeVars:
			free_var_names.append(Name(var))
		return InjectFrom(Const(3), CallFunc(GlobalFuncName('create_closure'),[GlobalFuncName(func_name), List(free_var_names)]))
	elif isinstance(ast, GlobalFuncName):
		return ast
	elif isinstance(ast, Return):
		return Return(closure(ast.value, functions, variables))
	elif isinstance(ast, List):
		newElem = []
		for elem in ast.nodes:
			newElem.append(closure(elem, functions, variables))
		return List(newElem)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((closure(item[0], functions, variables), closure(item[1], functions, variables)))
		return Dict(newItems)
	else:
		raise Exception("No AST match: " + str(ast))