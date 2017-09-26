import structs
class GraphNode():
	def __init__(self):
		self.color = None
		self.saturation = []
		self.edges = []
	def __str__(self):
		string = "["
		for edge in self.edges:
			string += edge.name
		string += "]"
		return "GraphNode(" + str(self.color) + ", " + str(self.saturation) + ", " + string + ")"

def createGraph(x86IR, variables):
	nodes = {"eax":GraphNode(), "ecx":GraphNode(), "edx":GraphNode()}
	for var in variables:
		nodes[var.name] = GraphNode()
	working = x86IR
	while (working != None):
		if working.operation == "movl":
			if isinstance(working.var2, structs.Var):
				for var in working.liveness:
					if not (working.var2 == var or working.var1 == var):
						pass
		working = working.next
	return nodes

