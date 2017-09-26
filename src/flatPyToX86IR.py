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
		elif node.operation == "Print":
			last = addInstruction(last, structs.x86IRNode("call print", node.input1, None))
		elif node.operation == "Assign":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
		elif node.operation == "Add":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			last = addInstruction(last, structs.x86IRNode("addl", node.input2, node.output))
		elif node.operation == "Neg":
			last = addInstruction(last, structs.x86IRNode("movl", node.input1, node.output))
			last = addInstruction(last, structs.x86IRNode("negl", node.output, None))
		elif node.operation == "Input":
			last = addInstruction(last, structs.x86IRNode("call input", node.input1, None))
		else:
			raise Exception("No flatAST match: " + str(node))
		node = node.next
	return structs.getFirst(last)
