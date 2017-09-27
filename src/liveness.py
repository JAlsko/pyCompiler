import structs

def setLiveness(flatAssem):
	working = structs.getLast(flatAssem)
	liveNow = set([])
	while working != None:
		working.liveness = set(liveNow)

		if working.operation == "movl":
			if isinstance(working.var2, structs.Var):
				liveNow.discard(working.var2.name)
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "call":
			liveNow.discard("eax")
			liveNow.discard("ecx")
			liveNow.discard("edx")
		elif working.operation == "addl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "pushl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "negl":
			pass
		else:
			raise Exception("No instruction match: " + str(working.operation))

		working = working.prev

