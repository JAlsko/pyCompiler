import structs

def createAssembly(targetFile, flatAssem, graph, numColors):
	with open(targetFile, "w") as outputFile:
		working = flatAssem
		outputFile.write(".globl main\n")
		outputFile.write("main:\n")
		outputFile.write("\tpushl %ebp\n")
		outputFile.write("\tmovl %esp, %ebp\n")
		outputFile.write("\tsubl $" + str(numColors * 4) + ", %esp\n")
		while working != None:
			if isinstance(working.var1, structs.Var) and isinstance(working.var2, structs.Var) and str(graph[working.var1.name].color) == str(graph[working.var2.name].color):
				working = working.next
			else:
				outputFile.write("\t" + working.operation + " ")
				if isinstance(working.var1, structs.Var):
					outputFile.write(str(graph[working.var1.name].color))
				elif working.operation == "call":
					outputFile.write(str(working.var1))
				else:
					outputFile.write("$" + str(working.var1))
				if isinstance(working.var2, structs.Var):
					outputFile.write(", " + str(graph[working.var2.name].color))
				elif working.var2 != None:
					outputFile.write(", " + str(working.var2))
				outputFile.write("\n")
				working = working.next
		outputFile.write("\tmovl $0, %eax\n")
		outputFile.write("\tleave\n")
		outputFile.write("\tret\n")
		outputFile.close()
