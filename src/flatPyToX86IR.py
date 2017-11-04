import structs

def addInstruction(last, new_instruction):
	if last != None:
		last.next = new_instruction
	new_instruction.prev = last
	return new_instruction

def createAssembly(flatAst, func_name):
	node = flatAst
	first = None
	last = None
	while node != None:
		if node.operation == "FunctionStart":
			for i in range(0, len(node.output)):
				last = addInstruction(last, structs.x86IRNode("movl", structs.Stack(str(4*(2+i)) + "(%ebp)"), node.output[i]))
		elif node.operation == "FunctionEnd":
			pass
		elif node.operation == "Assign":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
		elif node.operation == "Add":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			last = addInstruction(last, structs.x86IRNode("addl", node.input2, node.output))
		elif node.operation == "Neg":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			last = addInstruction(last, structs.x86IRNode("negl", node.output, None))
		elif node.operation == "InjectFrom":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			if node.input2 != 3:
				last = addInstruction(last, structs.x86IRNode("sall", 2, node.output))
				last = addInstruction(last, structs.x86IRNode("orl", node.input2, node.output))
			else:
				last = addInstruction(last, structs.x86IRNode("addl", 3, node.output))
		elif node.operation == "ProjectTo":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			if node.input2 != 3:
				last = addInstruction(last, structs.x86IRNode("sarl", 2, node.output))
			else:
				last = addInstruction(last, structs.x86IRNode("andl", -4, node.output))
		elif node.operation == "GetTag":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			last = addInstruction(last, structs.x86IRNode("andl", 3, node.output))
		elif node.operation == "IfExp":
			last = addInstruction(last, structs.x86IRNode("IfExp", node.input1, node.output))
			last.thenNext = createAssembly(node.thenNext, func_name)
			last.elseNext = createAssembly(node.elseNext, func_name)
		elif node.operation == "CompareEQ":
			if isinstance(node.input1, structs.Var):
				last = addInstruction(last, structs.x86IRNode("cmpl", node.input2, node.input1))
			else:
				last = addInstruction(last, structs.x86IRNode("cmpl", node.input1, node.input2))
			last = addInstruction(last, structs.x86IRNode("sete", structs.Var("al"), None))
			last = addInstruction(last, structs.x86IRNode("movzbl", structs.Var("al"), node.output))
		elif node.operation == "CompareNE":
			last = addInstruction(last, structs.x86IRNode("cmpl", node.input1, node.input2))
			last = addInstruction(last, structs.x86IRNode("setne", structs.Var("al"), None))
			last = addInstruction(last, structs.x86IRNode("movzbl", structs.Var("al"), node.output))
		elif node.operation == "Not":
			last = addInstruction(last, structs.x86IRNode("cmpl", 0, node.input1))
			last = addInstruction(last, structs.x86IRNode("sete", structs.Var("al"), None))
			last = addInstruction(last, structs.x86IRNode("movzbl", structs.Var("al"), node.output))
		elif node.operation == "CallFunc":
			for var in reversed(node.input2):
				last = addInstruction(last, structs.x86IRNode("pushl", var, None))
			last = addInstruction(last, structs.x86IRNode("call", node.input1, None))
			if node.output != None:
				last = addInstruction(last, structs.x86IRNode("movl", structs.Var("eax"), node.output))
			last = addInstruction(last, structs.x86IRNode("addl", 4*len(node.input2), structs.Stack("%esp")))
		elif node.operation == "Return":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, structs.Var("eax")))
			last = addInstruction(last, structs.x86IRNode("jmp", func_name + "_end", None))
		else:
			raise Exception("No flatAST match: " + str(node))
		node = node.next
	return structs.getFirst(last)
