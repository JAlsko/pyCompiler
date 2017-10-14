import structs

def createAssembly(targetFile, flatAssem, graph, numColors):
	ebx = False
	edi = False
	esi = False
	for key in graph:
		if graph[key].color == "%ebx":
			ebx = True
		elif graph[key].color == "%edi":
			edi = True
		elif graph[key].color == "%esi":
			esi = True
	
	with open(targetFile, "w") as outputFile:
		working = flatAssem
		outputFile.write(".globl main\n")
		outputFile.write("main:\n")
		outputFile.write("\tpushl %ebp\n")
		outputFile.write("\tmovl %esp, %ebp\n")
		if ebx:
			outputFile.write("\tmovl %ebx, -" + str(numColors * 4) + "(%ebp)\n")
			numColors += 1
		if edi:
			outputFile.write("\tmovl %edi, -" + str(numColors * 4) + "(%ebp)\n")
			numColors += 1
		if esi:
			outputFile.write("\tmovl %esi, -" + str(numColors * 4) + "(%ebp)\n")
			numColors += 1
		outputFile.write("\tsubl $" + str(numColors * 4) + ", %esp\n")
		while working != None:
			if isinstance(working.var1, structs.Var) and isinstance(working.var2, structs.Var) and str(graph[working.var1.name].color) == str(graph[working.var2.name].color) and working.operation == "movl":
				working = working.next
			else:
				outputFile.write("\t" + working.operation + " ")
				if isinstance(working.var1, structs.Var):
					if working.var1.name == "al":
						outputFile.write("%al")
					else:
						outputFile.write(str(graph[working.var1.name].color))
				elif working.operation in ["call", "jmp", "je"]:
					outputFile.write(str(working.var1))
				else:
					if working.var1 != None:
						if working.var1 == True:
							outputFile.write("$1")
						elif working.var1 == False:
							outputFile.write("$0")
						else:
							outputFile.write("$" + str(working.var1))
				if isinstance(working.var2, structs.Var):
					outputFile.write(", " + str(graph[working.var2.name].color))
				elif working.var2 != None:
					outputFile.write(", " + str(working.var2))
				outputFile.write("\n")
				working = working.next
		if esi:
			numColors -= 1
			outputFile.write("\tmovl -" + str(numColors * 4) + "(%ebp), %esi\n")
		if edi:
			numColors -= 1
			outputFile.write("\tmovl -" + str(numColors * 4) + "(%ebp), %edi\n")
		if ebx:
			numColors -= 1
			outputFile.write("\tmovl -" + str(numColors * 4) + "(%ebp), %ebx\n")
		outputFile.write("\tmovl $0, %eax\n")
		outputFile.write("\tleave\n")
		outputFile.write("\tret\n")
		outputFile.close()
