import structs

def checkSpills(flatAssem, graph, variables):
	registers = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]
	working = flatAssem
	retAssem = flatAssem
	unspillable = []
	while working != None:
		if isinstance(working.var1, structs.Var) and isinstance(working.var2, structs.Var):
			if not graph[working.var1.name].color in registers:
				if not graph[working.var2.name].color in registers:
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
