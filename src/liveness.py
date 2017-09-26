import structs

def setLiveness(flatAssem):
	working = structs.getLast(flatAssem)
	liveNow = set([])
	while working != None:
		if working.operation == "addl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1)
		elif working.operation == "movl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1)
			if isinstance(working.var2, structs.Var):
				liveNow.discard(working.var2)
		elif working.operation == "call print":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1)
		elif working.operation == "call input":
			if isinstance(working.var1, structs.Var):
				liveNow.discard(working.var1)
		elif working.operation == "negl":
			pass
		else:
			raise Exception("Failed to recognize instruction: " + str(working))

		working.liveness = set(liveNow)
		working = working.prev
