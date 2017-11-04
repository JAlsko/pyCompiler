import structs

def setLiveness(flatAssem, live):
	working = structs.getLast(flatAssem)
	liveNow = live
	while working != None:
		working.liveness = set(liveNow)

		if working.operation in ["movl", "movzbl"]:
			if isinstance(working.var2, structs.Var):
				liveNow.discard(working.var2.name)
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "cmpl":
			if isinstance(working.var2, structs.Var):
				liveNow.add(working.var2.name)
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "call":
			liveNow.discard("eax")
			liveNow.discard("ecx")
			liveNow.discard("edx")
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "addl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "sete":
			if isinstance(working.var1, structs.Var):
				liveNow.discard(working.var1.name)
		elif working.operation == "setne":
			if isinstance(working.var1, structs.Var):
				liveNow.discard(working.var1.name)
		elif working.operation == "orl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "pushl":
			if isinstance(working.var1, structs.Var):
				liveNow.add(working.var1.name)
		elif working.operation == "negl":
			pass
		elif working.operation == "notl":
			pass
		elif working.operation == "sall":
			pass
		elif working.operation == "sarl":
			pass
		elif working.operation == "andl":
			pass
		elif working.operation == "ret":
			pass
		elif working.operation == "leave":
			pass
		elif working.operation == "jmp":
			pass
		elif working.operation == "IfExp":
			thenLive = setLiveness(working.thenNext, liveNow)
			elseLive = setLiveness(working.elseNext, liveNow)
			liveNow = thenLive | elseLive
		else:
			raise Exception("No instruction match: " + str(working.operation))

		working = working.prev
	return liveNow

