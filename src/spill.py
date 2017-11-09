import structs

def checkSpills(flatAssem, graph, variables):
	registers = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]
	working = flatAssem
	retAssem = flatAssem
	unspillable = []
	while working != None:
		if working.operation in ["IfExp", "While"]:
			result = checkSpills(working.thenNext, graph, variables)
			working.thenNext = result[0]
			unspillable.extend(result[1])
			result = checkSpills(working.elseNext, graph, variables)
			working.elseNext = result[0]
			unspillable.extend(result[1])
		else:
			var1Stack = False
			var2Stack = False
			if isinstance(working.var1, structs.Stack):
				var1Stack = True
			elif isinstance(working.var1, structs.Var):
				if not graph[working.var1.name].color in registers:
					var1Stack = True
			if isinstance(working.var2, structs.Stack):
				var2Stack = True
			elif isinstance(working.var2, structs.Var):
				if not graph[working.var2.name].color in registers:
					var2Stack = True
			if var1Stack and var2Stack:
				new_var = structs.newVariable(variables, None)
				new_instr = structs.x86IRNode("movl", working.var1, new_var)
				new_instr.next = working
				new_instr.prev = working.prev
				working.var1 = new_var
				if working.prev != None:
					working.prev.next = new_instr
				else:
					retAssem = new_instr
				working.prev = new_instr
				unspillable.append(new_var)

		working = working.next

	return (retAssem, unspillable)
