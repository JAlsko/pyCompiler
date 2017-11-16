import compiler
from compiler.ast import *
from eStructs import *

def newVariable(variables):
	newVar = "d" + str(len(variables))
	variables.append(newVar)
	return newVar

def declassClass(ast, variables, tempName):
	if isinstance(ast, Stmt):
		newStmts = []
		for statement in ast.nodes:
			ret = declassClass(statement, variables, tempName)
			newStmts.append(ret)
		return Stmt(newStmts)
	elif isinstance(ast, Printnl):
		return Printnl([declassClass(ast.nodes[0], variables, tempName)], ast.dest)
	elif isinstance(ast, Assign):
		if isinstance(ast.nodes[0], AssName):
			return Discard(CallFunc(GlobalFuncName('set_attr'), [Name(tempName), String(ast.nodes[0].name), declassClass(ast.expr, variables, tempName)]))
		else:
			return Assign([declassClass(ast.nodes[0], variables, tempName)], declassClass(ast.expr, variables, tempName))
	elif isinstance(ast, Discard):
		return Discard(declassClass(ast.expr, variables, tempName))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, String):
		return ast
	elif isinstance(ast, GlobalFuncName):
		return ast
	elif isinstance(ast, Name):
		condition = CallFunc(GlobalFuncName('has_attr'), [Name(tempName), String(ast.name)])
		attr_get = CallFunc(GlobalFuncName('get_attr'), [Name(tempName), String(ast.name)])
		return IfExp(condition, attr_get, ast)
	elif isinstance(ast, AssName):
		return ast
	elif isinstance(ast, Add):
		return Add((declassClass(ast.left, variables, tempName), declassClass(ast.right, variables, tempName)))
	elif isinstance(ast, Compare):
		return Compare(declassClass(ast.expr, variables, tempName),[(ast.ops[0][0],declassClass(ast.ops[0][1], variables, tempName))])
	elif isinstance(ast, And):
		return And([declassClass(ast.nodes[0], variables, tempName),declassClass(ast.nodes[1], variables, tempName)])
	elif isinstance(ast, Or):
		return Or([declassClass(ast.nodes[0], variables, tempName),declassClass(ast.nodes[1], variables, tempName)])
	elif isinstance(ast, UnarySub):
		return UnarySub(declassClass(ast.expr, variables, tempName))
	elif isinstance(ast, Not):
		return Not(declassClass(ast.expr, variables, tempName))
	elif isinstance(ast, CallFunc):
		uniqArgs = []
		for arg in ast.args:
			uniqArgs.append(declassClass(arg, variables, tempName))
		return CallFunc(declassClass(ast.node, variables, tempName), uniqArgs)
	elif isinstance(ast, List):
		newNodes = []
		for node in ast.nodes:
			newNodes.append(declassClass(node, variables, tempName))
		return List(newNodes)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((declassClass(item[0], variables, tempName),declassClass(item[1], variables, tempName)))
		return Dict(newItems)
	elif isinstance(ast, Subscript):
		return Subscript(declassClass(ast.expr, variables, tempName), ast.flags, [declassClass(ast.subs[0], variables, tempName)])
	elif isinstance(ast, IfExp):
		return IfExp(declassClass(ast.test, variables, tempName), declassClass(ast.then, variables, tempName), declassClass(ast.else_, variables, tempName))
	elif isinstance(ast, Return):
		return Return(declassClass(ast.value, variables, tempName))
	elif isinstance(ast, Lambda):
		return Lambda(ast.argnames, [], 0, ast.code)
	elif isinstance(ast, If):
		return If([(declassClass(ast.tests[0][0], variables, tempName), declassClass(ast.tests[0][1], variables, tempName))], declassClass(ast.else_, variables, tempName))
	elif isinstance(ast, While):
		return While(declassClass(ast.test, variables, tempName), declassClass(ast.body, variables, tempName), None)
	else:
		raise Exception("No AST match: " + str(ast))

def declassify(ast, variables):
	if isinstance(ast, Module):
		return Module(None, declassify(ast.node, variables))
	elif isinstance(ast, Stmt):
		newStmts = []
		for statement in ast.nodes:
			ret = declassify(statement, variables)
			if isinstance(ret, list):
				newStmts.extend(ret)
			else:
				newStmts.append(ret)
		return Stmt(newStmts)
	elif isinstance(ast, Printnl):
		return Printnl([declassify(ast.nodes[0], variables)], ast.dest)
	elif isinstance(ast, Assign):
		if isinstance(ast.nodes[0], AssAttr):
			return Discard(CallFunc(GlobalFuncName('set_attr'), [ast.nodes[0].expr, String(ast.nodes[0].attrname), declassify(ast.expr, variables)]))
		else:
			return Assign([declassify(ast.nodes[0], variables)], declassify(ast.expr, variables))
	elif isinstance(ast, Discard):
		return Discard(declassify(ast.expr, variables))
	elif isinstance(ast, Const):
		return ast
	elif isinstance(ast, Name):
		return ast
	elif isinstance(ast, AssName):
		return ast
	elif isinstance(ast, Add):
		return Add((declassify(ast.left, variables), declassify(ast.right, variables)))
	elif isinstance(ast, Compare):
		return Compare(declassify(ast.expr, variables),[(ast.ops[0][0],declassify(ast.ops[0][1], variables))])
	elif isinstance(ast, And):
		return And([declassify(ast.nodes[0], variables),declassify(ast.nodes[1], variables)])
	elif isinstance(ast, Or):
		return Or([declassify(ast.nodes[0], variables),declassify(ast.nodes[1], variables)])
	elif isinstance(ast, UnarySub):
		return UnarySub(declassify(ast.expr, variables))
	elif isinstance(ast, Not):
		return Not(declassify(ast.expr, variables))
	elif isinstance(ast, CallFunc):
		if not (isinstance(ast.node, Name) and ast.node.name == 'input'):
			declassArgs = []
			newVarF = newVariable(variables)
			needLet = [(newVarF, declassify(ast.node, variables))]
			for arg in ast.args:
				newArg = declassify(arg, variables)
				newVar = newVariable(variables)
				declassArgs.append(Name(newVar))
				needLet.append((newVar, newArg))
			Condition = CallFunc(GlobalFuncName("is_class"), [Name(newVarF)])
			newVar = newVariable(variables)
			condition0 = CallFunc(GlobalFuncName('has_attr'), [Name(newVarF), String("__init__")])
			then0 = Let(Name("dummy"), CallFunc(CallFunc(GlobalFuncName("get_function"), [CallFunc(GlobalFuncName("get_attr"), [Name(newVarF), String('__init__')])]), [Name(newVar)] + declassArgs), Name(newVar))
			else0 = Name(newVar)
			class_create_content = IfExp(condition0, then0, else0)
			then = Let(Name(newVar), CallFunc(GlobalFuncName("create_object"), [Name(newVarF)]), class_create_content)
			Condition2 = CallFunc(GlobalFuncName("is_bound_method"), [Name(newVarF)])
			bound_arg_list = [CallFunc(GlobalFuncName("get_receiver"), [Name(newVarF)])]
			bound_arg_list.extend(declassArgs)
			then2 = CallFunc(CallFunc(GlobalFuncName("get_function"), [Name(newVarF)]), bound_arg_list)
			Condition3 = CallFunc(GlobalFuncName("is_unbound_method"), [Name(newVarF)])
			then3 = CallFunc(CallFunc(GlobalFuncName("get_function"), [Name(newVarF)]), declassArgs)
			else3 = CallFunc(declassify(Name(newVarF), variables), declassArgs)
			else2 = IfExp(Condition3, then3, else3)
			else1 = IfExp(Condition2, then2, else2)
			content = IfExp(Condition, then, else1)
			for elem in needLet:
				content = Let(Name(elem[0]), elem[1], content)
			return content
		else:
			return ast
	elif isinstance(ast, List):
		newNodes = []
		for node in ast.nodes:
			newNodes.append(declassify(node, variables))
		return List(newNodes)
	elif isinstance(ast, Dict):
		newItems = []
		for item in ast.items:
			newItems.append((declassify(item[0], variables),declassify(item[1], variables)))
		return Dict(newItems)
	elif isinstance(ast, Subscript):
		return Subscript(declassify(ast.expr, variables), ast.flags, [declassify(ast.subs[0], variables)])
	elif isinstance(ast, IfExp):
		return IfExp(declassify(ast.test, variables), declassify(ast.then, variables), declassify(ast.else_, variables))
	elif isinstance(ast, Return):
		return Return(declassify(ast.value, variables))
	elif isinstance(ast, Function):
		#return Function(None, ast.name, ast.argnames, [], 0, None, declassify(ast.code, variables))
		return Assign([AssName(ast.name, 'OP_ASSIGN')],Lambda(ast.argnames, ast.defaults, ast.flags, declassify(ast.code, variables)))
	elif isinstance(ast, Lambda):
		#return Lambda(ast.argnames, [], 0, declassify(ast.code, variables))
		return Lambda(ast.argnames, ast.defaults, ast.flags, Stmt([Return(declassify(ast.code, variables))]))
	elif isinstance(ast, If):
		return If([(declassify(ast.tests[0][0], variables), declassify(ast.tests[0][1], variables))], declassify(ast.else_, variables))
	elif isinstance(ast, While):
		return While(declassify(ast.test, variables), declassify(ast.body, variables), None)
	elif isinstance(ast, Class):
		tmp = newVariable(variables)
		newStmts = []
		newStmts.append(Assign([AssName(tmp,'OP_ASSIGN')],CallFunc(GlobalFuncName('create_class'), [List([])])))
		code = declassify(ast.code, variables)
		code = declassClass(code, variables, tmp)
		for stmt in code.nodes:
			newStmts.append(stmt)
		newStmts.append(Assign([AssName(ast.name,'OP_ASSIGN')],Name(tmp)))
		return newStmts
	elif isinstance(ast, Getattr):
		return CallFunc(GlobalFuncName('get_attr'), [declassify(ast.expr, variables), String(ast.attrname)])
	else:
		raise Exception("No AST match: " + str(ast))