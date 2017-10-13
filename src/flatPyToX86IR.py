import structs

def addInstruction(last, new_instruction):
	if last != None:
		last.next = new_instruction
	new_instruction.prev = last
	return new_instruction

def createAssembly(flatAst):
	node = flatAst
	first = None
	last = None
	while node != None:
		if node.operation == "FunctionStart":
			pass
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
			pass
		elif node.operation == "ProjectTo":
			pass
		elif node.operation == "GetTag":
			pass
		elif node.operation == "IfExp":
			last = addInstruction(last, structs.x86IRNode("IfExp", node.input1, node.output))
			last.thenNext = createAssembly(node.thenNext)
			last.thenNext.prev = last
			last.elseNext = createAssembly(node.elseNext)
			last.elseNext.prev = last
		elif node.operation == "CompareEQ":
			pass
		elif node.operation == "CompareNE":
			pass
		elif node.operation == "Not":
			pass
		elif node.operation == "CallFunc":
			for var in reversed(node.input2):
				last = addInstruction(last, structs.x86IRNode("pushl", var, None))
			last = addInstruction(last, structs.x86IRNode("call", node.input1, None))
			last = addInstruction(last, structs.x86IRNode("movl", structs.Var("eax"), node.output))
			last = addInstruction(last, structs.x86IRNode("addl", 4*len(node.input2), structs.Esp()))

		else:
			raise Exception("No flatAST match: " + str(node))
		node = node.next
	return structs.getFirst(last)
