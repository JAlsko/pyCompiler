import compiler
from compiler.ast import *
from eStructs import *

def declassify(ast):
	if isinstance(ast, Module):
		return Module(None, declassify(ast.node))
	elif isinstance(ast, Stmt):
		newStmts = []
		for statement in ast.nodes:
			newStmts.append(declassify(statement))
		return Stmt(newStmts)
	elif isinstance(ast, Printnl):
		return Printnl([declassify(ast.nodes[0])], ast.dest)
	elif isinstance(ast, Assign):
		if isinstance(ast.nodes[0], AssAttr):
			return Discard(CallFunc(GlobalFuncName('set_attr'), [ast.nodes[0].expr, String(ast.nodes[0].attrname), declassify(ast.expr)]))
		else:
			return Assign([declassify(ast.nodes[0])], declassify(ast.expr))
	elif isinstance(ast, Discard):
		return Discard(declassify(ast.expr))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Name):
		return ast
	elif isinstance(ast, AssName):
		return ast
	elif isinstance(ast, Add):
		return Add((declassify(ast.left), declassify(ast.right)))
	elif isinstance(ast, Compare):
		return Compare(declassify(ast.expr),[(ast.ops[0][0],declassify(ast.ops[0][1]))])
	elif isinstance(ast, And):
		return And([declassify(ast.nodes[0]),declassify(ast.nodes[1])])
	elif isinstance(ast, Or):
		return Or([declassify(ast.nodes[0]),declassify(ast.nodes[1])])
	elif isinstance(ast, UnarySub):
		return UnarySub(declassify(ast.expr))
	elif isinstance(ast, Not):
		return Not(declassify(ast.expr))
	elif isinstance(ast, CallFunc):
		uniqArgs = []
		for arg in ast.args:
			uniqArgs.append(declassify(arg))
		return CallFunc(declassify(ast.node), uniqArgs)
	elif isinstance(ast, List):
		newNodes = []
		for node in ast.nodes:
			newNodes.append(declassify(node))
		return List(newNodes)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((declassify(item[0]),declassify(item[1])))
		return Dict(newItems)
	elif isinstance(ast, Subscript):
		return Subscript(declassify(ast.expr), ast.flags, [declassify(ast.subs[0])])
	elif isinstance(ast, IfExp):
		return IfExp(declassify(ast.test), declassify(ast.then), declassify(ast.else_))
	elif isinstance(ast, Return):
		return Return(declassify(ast.value))
	elif isinstance(ast, Function):
		return Function(None, ast.name, ast.argnames, [], 0, None, declassify(ast.code))
	elif isinstance(ast, Lambda):
		return Lambda(ast.argnames, [], 0, declassify(ast.code))
	elif isinstance(ast, If):
		return If([(declassify(ast.tests[0][0]), declassify(ast.tests[0][1]))], declassify(ast.else_))
	elif isinstance(ast, While):
		return While(declassify(ast.test), declassify(ast.body), None)
	elif isinstance(ast, Class):
		return Assign([AssName(ast.name,'OP_ASSIGN')],CallFunc(GlobalFuncName('create_class'), [List([])]))
	elif isinstance(ast, Getattr):
		return CallFunc(GlobalFuncName('get_attr'), [ast.expr, String(ast.attrname)])
	else:
		raise Exception("No AST match: " + str(ast))