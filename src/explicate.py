import compiler
from compiler.ast import *
import structs

'''
Need Let(x, e1, e2), GetTag(x), InjectFrom(TAG,e), and ProjectTo(TAG,e)
'''

class Let():
	def __init__(self, var, rhs, body):
		self.var = var
		self.rhs = rhs
		self.body = body
	def __str__(self):
		return "Let(" + str(self.var) + ", " + str(self.rhs) + ", " + str(self.body) + ")"

class GetTag():
	def __init__(self, arg):
		self.arg = arg
	def __str__(self):
		return "GetTag(" + str(self.x) + ")"

class ProjectTo(node):
	def __init__(self, typ, arg):
		self.typ = typ
		self.arg = arg

class InjectFrom(node):
	def __init__(self, typ, arg):
		self.typ = typ
		self.arg = arg

def explicate(ast, variables):
	if isinstance(ast, Add):
		x = structs.newVariable()
		y = structs.newVariable()
		working = Let(x, ast.left, Let(y, ast.right, IfExpr(And(Eq(GetTag(x), INT), GetTag(y), INT), AddInt(x, y)))