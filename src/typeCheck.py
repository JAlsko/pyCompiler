import compiler
from compiler.ast import *
from eStructs import *

INT = 0
BOOL = 1
BIG = 3
PYOBJ = 4
NONE = -1
FUNCRET = -2

def typeCheck(ast, variables):
	recived_types = []
	if isinstance(ast, Module):
		valid_type = NONE
		recived_types.append(typeCheck(ast.node, variables))
		ret = NONE
	elif isinstance(ast, Stmt):
		valid_type = NONE
		for i in ast.nodes:
			recived_types.append(typeCheck(i, variables))
		ret = NONE
	elif isinstance(ast, Assign):
		valid_type = PYOBJ
		typ = typeCheck(ast.expr, variables)
		recived_types.append(typ)
		variables[ast.nodes[0].name] = typ
		ret = NONE
	elif isinstance(ast, Discard):
		valid_type = PYOBJ
		recived_types.append(typeCheck(ast.expr, variables))
		ret = NONE
	elif isinstance(ast, Const):
		return INT
	elif isinstance(ast, Bool):
		return BOOL
	elif isinstance(ast, Name):
		return variables[ast.name]
	elif isinstance(ast, Add):
		valid_type = INT
		recived_types.append(typeCheck(ast.left, variables))
		recived_types.append(typeCheck(ast.right, variables))
		ret = INT
	elif isinstance(ast, Compare):
		valid_type = INT
		typ1 = typeCheck(ast.expr, variables)
		typ2 = typeCheck(ast.ops[0][1], variables)
		if typ1 == typ2:
			return BOOL
		elif typ1 == FUNCRET:
			return BOOL
		elif typ2 == FUNCRET:
			return BOOL
	elif isinstance(ast, UnarySub):
		valid_type = INT
		recived_types.append(typeCheck(ast.expr, variables))
		ret = INT
	elif isinstance(ast, Not):
		valid_type = BOOL
		recived_types.append(typeCheck(ast.expr, variables))
		ret = BOOL
	elif isinstance(ast, CallFunc):
		for i in ast.args:
			typeCheck(i, variables)
		return FUNCRET
	elif isinstance(ast, List):
		valid_type = PYOBJ
		for i in ast.nodes:
			recived_types.append(typeCheck(i, variables))
		ret = PYOBJ
	elif isinstance(ast, Dict):
		valid_type = PYOBJ
		for i in ast.items:
			recived_types.append(typeCheck(i[0], variables))
			recived_types.append(typeCheck(i[1], variables))
		ret = PYOBJ
	elif isinstance(ast, IfExp):
		typ = typeCheck(ast.test, variables)
		if typ != BOOL:
			raise Exception("Type mis-match:" + str(ast) + ", " + str(typ) + ", " + str(BOOL))
		typ1 = typeCheck(ast.then, variables)
		typ2 = typeCheck(ast.else_, variables)
		if typ1 == typ2:
			return typ1
		elif typ1 == FUNCRET:
			return typ2
		elif typ2 == FUNCRET:
			return typ1
		else:
			raise Exception("Type mis-match returns:" + str(ast) + ", " + str(typ1) + ", " + str(typ2))
	elif isinstance(ast, Let):
		typ = typeCheck(ast.rhs, variables)
		recived_types.append(typ)
		variables[ast.var.name] = typ
		return typeCheck(ast.body, variables)
	elif isinstance(ast, InjectFrom):
		valid_type = ast.typ.value
		recived_types.append(typeCheck(ast.arg, variables))
		ret = PYOBJ
	elif isinstance(ast, ProjectTo):
		valid_type = PYOBJ
		recived_types.append(typeCheck(ast.arg, variables))
		ret = ast.typ.value
	elif isinstance(ast, GetTag):
		valid_type = PYOBJ
		recived_types.append(typeCheck(ast.arg, variables))
		ret = INT
	else:
		raise Exception("No AST match: " + str(ast))

	for i in recived_types:
		if not i in [valid_type, FUNCRET]:
			raise Exception("Type mis-match:" + str(ast) + ", " + str(i) + ", " + str(valid_type))
	return ret

