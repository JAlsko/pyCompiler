class AddInt():
	def __init__(self, e1, e2):
		self.e1 = e1
		self.e2 = e2
	def __str__(self):
		return "AddInt(" + str(e1) + ", " + str(e2) + ")"

class AddBool():
	def __init__(self, e1, e2):
		self.e1 = e1
		self.e2 = e2
	def __str__(self):
		return "AddBool(" + str(e1) + ", " + str(e2) + ")"

class AddBig():
	def __init__(self, e1, e2):
		self.e1 = e1
		self.e2 = e2
	def __str__(self):
		return "AddBig(" + str(e1) + ", " + str(e2) + ")"

class Let():
	def __init__(self, var, rhs, body):
		self.var = var
		self.rhs = rhs
		self.body = body
	def __str__(self):
		return "Let(" + str(self.var) + ", " + str(self.rhs) + ", " + str(self.body) + ")"

class GetTag():
	def __init__(self, arg):
		self.arg = arg
	def __str__(self):
		return "GetTag(" + str(self.x) + ")"

class ProjectTo():
	def __init__(self, typ, arg):
		self.typ = typ
		self.arg = arg

class InjectFrom():
	def __init__(self, typ, arg):
		self.typ = typ
		self.arg = arg