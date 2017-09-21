import structs

def createAssembly(targetFile, flatAst):
	with open(targetFile, "w") as outputFile:
		node = flatAst
		outputFile.write(".globl main\n")
		outputFile.write("main:\n")
		while node != None:
			if node.operation == "FunctionStart":
				outputFile.write("\tpushl %ebp\n")
				outputFile.write("\tmovl %esp, %ebp\n")
				outputFile.write("\tsubl $" + str(node.input1* 4) + ", %esp\n")
			elif node.operation == "FunctionEnd":
				#outputFile.write("\taddl $" + str(node.input1* 4) + ", %esp\n")
				outputFile.write("\tmovl $0, %eax\n")
				outputFile.write("\tleave\n")
				outputFile.write("\tret\n")
			elif node.operation == "Print":
				if isinstance(node.input1, structs.Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", %eax\n")
				outputFile.write("\tpushl %eax\n")
				outputFile.write("\tcall print_int_nl\n")
				outputFile.write("\taddl $4, %esp\n")
			elif node.operation == "Assign":
				if isinstance(node.input1, structs.Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
					outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Add":
				if isinstance(node.input1, structs.Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", %eax\n")
				if isinstance(node.input2, structs.Var):
					outputFile.write("\taddl -" + str((node.input2.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\taddl $" + str(node.input2) + ", %eax\n")
				outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Neg":
				if isinstance(node.input1, structs.Var):
					outputFile.write("\tmovl -" + str((node.input1.name+1)*4) + "(%ebp), %eax\n")
				else:
					outputFile.write("\tmovl $" + str(node.input1) + ", %eax\n")
				outputFile.write("\tnegl %eax\n")
				outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			elif node.operation == "Input":
				outputFile.write("\tcall input\n")
				outputFile.write("\tmovl %eax, -" + str((node.output.name+1)*4) + "(%ebp)\n")
			else:
				raise Exception("No flatAST match: " + str(node))
			
			node = node.next
		outputFile.close()
