import structs
class GraphNode():
	def __init__(self, _unspillable):
		self.color = None
		self.saturation = set([])
		self.edges = set([])
		self.unspillable = _unspillable
	def __str__(self):
		return "GraphNode(" + str(self.color) + ", " + str(self.saturation) + ", " + str(self.unspillable) + ", " + str(self.edges) + ")"

def createGraph(x86IR, variables, unspillable):
	nodes = {"eax":GraphNode(True), "ecx":GraphNode(True), "edx":GraphNode(True)}
	for var in variables:
		spill = False
		if var in unspillable:
			spill = True
		nodes[var.name] = GraphNode(True)
	working = x86IR
	while (working != None):
		if working.operation == "movl":
			if isinstance(working.var2, structs.Var):
				for var in working.liveness:
					if not (working.var2.name == var):
						if isinstance(working.var1, structs.Var):
							if not working.var1.name == var:
								nodes[working.var2.name].edges.add(var)
								nodes[var].edges.add(working.var2.name)
						else:
							nodes[working.var2.name].edges.add(var)
							nodes[var].edges.add(working.var2.name)
		elif working.operation == "addl":
			if isinstance(working.var2, structs.Var):
				for var in working.liveness:
					if not (working.var2.name == var):
						nodes[working.var2.name].edges.add(var)
						nodes[var].edges.add(working.var2.name)
		elif working.operation == "negl":
			if isinstance(working.var1, structs.Var):
				for var in working.liveness:
					if not (working.var1.name == var):
						nodes[working.var1.name].edges.add(var)
						nodes[var].edges.add(working.var1.name)
		elif working.operation == "call":
			for var in working.liveness:
				nodes[var].edges.add("eax")
				nodes[var].edges.add("ecx")
				nodes[var].edges.add("edx")
				nodes["eax"].edges.add(var)
				nodes["ecx"].edges.add(var)
				nodes["edx"].edges.add(var)
		working = working.next
	return nodes

def color(saturation, colors):
	for color in colors:
		if color not in saturation:
			return color
	new_color = "-" + str((len(colors) - 5)*4) + "(%ebp)"
	colors.append(new_color)
	return new_color

def saturate(node, color, nodes):
	node.color = color
	for nodekey in node.edges:
		nodes[nodekey].saturation.add(color)

def colorGraph(nodes):
	colors = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]
	saturate(nodes["eax"],"%eax", nodes)
	saturate(nodes["ecx"],"%ecx", nodes)
	saturate(nodes["edx"],"%edx", nodes)

	while True:
		max_saturation = (False, -1)
		next_node = None
		for node in nodes:
			if nodes[node].color == None:
				if (nodes[node].unspillable, len(nodes[node].saturation)) > max_saturation:
					max_saturation = (nodes[node].unspillable, len(nodes[node].saturation))
					next_node = node
		if next_node == None:
			break
		saturate(nodes[next_node], color(nodes[next_node].saturation, colors), nodes)
	return len(colors) - 6
