import structs

def createAssembly(targetFile, flatAssem, graph):
	with open(targetFile, "w") as outputFile:
		working = flatAssem
		outputFile.write(".globl main\n")
		outputFile.write("main:\n")
		while working != None:
			outputFile.write(working.operation + " ")
			if isinstance(working.var1, structs.Var):
				outputFile.write(str(graph[working.var1.name].color))
			else:
				outputFile.write("$" + str(working.var1))
			if isinstance(working.var2, structs.Var):
				outputFile.write(", " + str(graph[working.var2.name].color))
			elif working.var2 != None:
				outputFile.write(", " + str(working.var2))
			outputFile.write("\n")
			working = working.next
		outputFile.write("leave\n")
		outputFile.write("ret")
		outputFile.close()
