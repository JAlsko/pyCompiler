import structs
import eStructs

def createAssembly(targetFile, flatAssem, graph, numColors):
	with open(targetFile, "w") as outputFile:
		outputFile.write(".globl main\n")
		for func in flatAssem:
			ebx = False
			edi = False
			esi = False
			for key in graph[func]:
				if graph[func][key].color == "%ebx":
					ebx = True
				elif graph[func][key].color == "%edi":
					edi = True
				elif graph[func][key].color == "%esi":
					esi = True
				working = flatAssem[func]
			outputFile.write(func + ":\n")
			outputFile.write("\tpushl %ebp\n")
			outputFile.write("\tmovl %esp, %ebp\n")
			print numColors[func]
			outputFile.write("\tsubl $" + str(numColors[func] * 4) + ", %esp\n")
			numColors[func] += 1
			if ebx:
				outputFile.write("\tmovl %ebx, -" + str(numColors[func] * 4) + "(%ebp)\n")
				numColors[func] += 1
			if edi:
				outputFile.write("\tmovl %edi, -" + str(numColors[func] * 4) + "(%ebp)\n")
				numColors[func] += 1
			if esi:
				outputFile.write("\tmovl %esi, -" + str(numColors[func] * 4) + "(%ebp)\n")
				numColors[func] += 1
			while working != None:
				if isinstance(working.var1, structs.Var) and isinstance(working.var2, structs.Var) and str(graph[func][working.var1.name].color) == str(graph[func][working.var2.name].color) and working.operation == "movl":
					working = working.next
				else:
					outputFile.write("\t" + working.operation + " ")
					if working.operation == "call":
						if isinstance(working.var1, structs.Var):
							outputFile.write("* ")
							outputFile.write(str(graph[func][working.var1.name].color))
						else:
							outputFile.write(str(working.var1.name))
					elif isinstance(working.var1, structs.Var):
						if working.var1.name == "al":
							outputFile.write("%al")
						else:
							outputFile.write(str(graph[func][working.var1.name].color))
					elif isinstance(working.var1, eStructs.GlobalFuncName):
						outputFile.write(str("$"))	
						outputFile.write(str(working.var1.name))	
					elif isinstance(working.var1, structs.Stack):
						outputFile.write(str(working.var1.name))
					elif working.operation in ["jmp", "je"]:
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
						outputFile.write(", " + str(graph[func][working.var2.name].color))
					elif working.var2 != None:
						outputFile.write(", " + str(working.var2.name))
					outputFile.write("\n")
					working = working.next
			outputFile.write("\tmovl $0, %eax\n")
			outputFile.write("\t" + func + "_end:\n")
			if esi:
				numColors[func] -= 1
				outputFile.write("\tmovl -" + str(numColors[func] * 4) + "(%ebp), %esi\n")
			if edi:
				numColors[func] -= 1
				outputFile.write("\tmovl -" + str(numColors[func] * 4) + "(%ebp), %edi\n")
			if ebx:
				numColors[func] -= 1
				outputFile.write("\tmovl -" + str(numColors[func] * 4) + "(%ebp), %ebx\n")
			outputFile.write("\tleave\n")
			outputFile.write("\tret\n")
		outputFile.close()
