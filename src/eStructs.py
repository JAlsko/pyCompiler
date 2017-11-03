class Bool():
	def __init__(self, val):
		self.value = val
	def __str__(self):
		return "Bool(" + str(self.value) + ")"
	def __repr__(self):
		return "Bool(" + str(self.value) + ")"

class GlobalFuncName():
	def __init__(self, _name):
		self.name = _name
	def __str__(self):
		return "GlobalFuncName(" + str(self.name) + ")"
	def __repr__(self):
		return "GlobalFuncName(" + str(self.name) + ")"

class Let():
	def __init__(self, var, rhs, body):
		self.var = var
		self.rhs = rhs
		self.body = body
	def __str__(self):
		return "Let(" + str(self.var) + ", " + str(self.rhs) + ", " + str(self.body) + ")"
	def __repr__(self):
		return "Let(" + str(self.var) + ", " + str(self.rhs) + ", " + str(self.body) + ")"

class GetTag():
	def __init__(self, arg):
		self.arg = arg
	def __str__(self):
		return "GetTag(" + str(self.arg) + ")"
	def __repr__(self):
		return "GetTag(" + str(self.arg) + ")"

class ProjectTo():
	def __init__(self, typ, arg):
		self.typ = typ
		self.arg = arg
	def __str__(self):
		return "ProjectTo(" + str(self.typ) + ", " + str(self.arg) + ")"
	def __repr__(self):
		return "ProjectTo(" + str(self.typ) + ", " + str(self.arg) + ")"

class InjectFrom():
	def __init__(self, typ, arg):
		self.typ = typ
		self.arg = arg
	def __str__(self):
		return "InjectFrom(" + str(self.typ) + ", " + str(self.arg) + ")"
	def __repr__(self):
		return "InjectFrom(" + str(self.typ) + ", " + str(self.arg) + ")"