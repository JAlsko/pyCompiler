import structs
class GraphNode():
	def __init__(self, _unspillable):
		self.color = None
		self.saturation = set([])
		self.edges = set([])
		self.unspillable = _unspillable
		self.qkey = None
	def __str__(self):
		return "GraphNode(" + str(self.color) + ", " + str(self.saturation) + ", " + str(self.unspillable) + ", " + str(self.edges) + ")"

class heapElement():
	def __init__(self, object_):
		self.value = 0
		self.object = object_
	def __repr__(self):
		return "HE(" + str(self.value) + "," + str(self.object) + ")"

def insertHeap(heap, obj, value):
	heap.append(heapElement(obj))
	return increment(heap, len(heap) - 1, value)

def increment(heap, loc, new_value):
	parent_loc = ((loc + 1) / 2) - 1
	if parent_loc != -1 and new_value > heap[parent_loc].value:
		holder = heap[parent_loc]
		heap[parent_loc] = heap[loc]
		heap[loc] = holder
		return increment(heap, parent_loc, new_value)
	else:
		heap[loc].value = new_value
		return loc

def pop(heap):
	if not heap:
		return None
	else:
		result = heap[0].object
		heap[0] = heap[len(heap) - 1]
		del heap[-1]
		if heap:
			shiftDown(heap, 0)
		return result

def shiftDown(heap, loc):
	leftLoc = loc * 2 + 1
	rightLoc = loc * 2 + 2
	if leftLoc > (len(heap) - 1):
		leftVal = 0
		rightVal = 0
	elif leftLoc == (len(heap) - 1):
		leftVal = heap[leftLoc].value
		rightVal = 0
	else:
		leftVal = heap[leftLoc].value
		rightVal = heap[rightLoc].value
	value = heap[loc].value
	if leftVal > value:
		if leftVal > rightVal:
			heapSwap(heap, loc, leftLoc)
			shiftDown(heap, leftLoc)
		else:
			heapSwap(heap, loc, rightLoc)
			shiftDown(heap, rightLoc)
	elif rightVal > value:
		heapSwap(heap, loc, rightLoc)
		shiftDown(heap, rightLoc)
	updateLocation(heap, loc)


def heapSwap(heap, loc1, loc2):
	holder = heap[loc1]
	heap[loc1] = heap[loc2]
	heap[loc2] = holder



def updateLocation(heap, loc):
	pass


def createGraph(x86IR, variables, unspillable):
	nodes = {"eax":GraphNode(True), "ecx":GraphNode(True), "edx":GraphNode(True), "al":GraphNode(True), "cl":GraphNode(True)}
	nodes["eax"].edges.add(nodes["al"])
	nodes["al"].edges.add(nodes["eax"])	
	nodes["ecx"].edges.add(nodes["cl"])
	nodes["cl"].edges.add(nodes["ecx"])

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
				nodes[var].edges.add("al")
				nodes[var].edges.add("ecx")
				nodes[var].edges.add("cl")
				nodes[var].edges.add("edx")
				nodes["eax"].edges.add(var)
				nodes["al"].edges.add(var)
				nodes["ecx"].edges.add(var)
				nodes["cl"].edges.add(var)
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
	saturate(nodes["al"],"%eax", nodes)
	saturate(nodes["ecx"],"%ecx", nodes)
	saturate(nodes["cl"],"%ecx", nodes)
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
