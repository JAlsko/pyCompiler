import structs
class GraphNode():
	def __init__(self, _unspillable):
		self.color = None
		self.saturation = set([])
		self.edges = set([])
		self.unspillable = _unspillable
		self.qkey = -1
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
	if loc != -1:
		parent_loc = ((loc + 1) / 2) - 1
		if parent_loc != -1 and new_value > heap[parent_loc].value:
			heapSwap(heap, parent_loc, loc)
			updateLocation(heap, loc)
			return increment(heap, parent_loc, new_value)
		else:
			heap[loc].value = new_value
			updateLocation(heap, loc)
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
	heap[loc].object.qkey = loc;

def createGraphWrapper(x86IR, variables, unspillable):
	nodes = {"eax":GraphNode(True), "ecx":GraphNode(True), "edx":GraphNode(True), "al":GraphNode(True)}

	for var in variables:
		spill = False
		if var in unspillable:
			spill = True
		nodes[var.name] = GraphNode(True)
	createGraph(x86IR, nodes)
	return nodes

def addEdge(var1, var2, nodes):
	nodes[var1].edges.add(var2)
	nodes[var2].edges.add(var1)

def addEdges(modVar, liveness, nodes):
	if isinstance(modVar, structs.Var):
		for var in liveness:
			if not (modVar.name == var):
				addEdge(modVar.name, var, nodes)

def createGraph(x86IR, nodes):
	working = x86IR
	while (working != None):
		if working.operation in ["movl", "movzbl"]:
			if isinstance(working.var2, structs.Var):
				for var in working.liveness:
					if not (working.var2.name == var):
						if isinstance(working.var1, structs.Var):
							if not working.var1.name == var:
								addEdge(working.var2.name, var, nodes)
						else:
							addEdge(working.var2.name, var, nodes)
		elif working.operation == "IfExp":
			addEdges(working.var1, working.liveness, nodes)
			createGraph(working.thenNext, nodes)
			createGraph(working.elseNext, nodes)
		elif working.operation in ["addl", "andl", "sall", "sarl", "orl"]:
			addEdges(working.var2, working.liveness, nodes)
		elif working.operation in ["negl", "notl", "sete", "setne"]:
			addEdges(working.var1, working.liveness, nodes)
		elif working.operation == "call":
			for var in working.liveness:
				nodes[var].edges.add("eax")
				nodes[var].edges.add("ecx")
				nodes[var].edges.add("edx")
				nodes["eax"].edges.add(var)
				nodes["ecx"].edges.add(var)
				nodes["edx"].edges.add(var)
		working = working.next

def color(saturation, colors):
	for color in colors:
		if color not in saturation:
			return color
	new_color = "-" + str((len(colors) - 5)*4) + "(%ebp)"
	colors.append(new_color)
	return new_color

def saturate(node, color, nodes, queue):
	node.color = color
	for nodekey in node.edges:
		nodes[nodekey].saturation.add(color)
		increment(queue, nodes[nodekey].qkey, (nodes[nodekey].unspillable, len(nodes[nodekey].saturation)))

def colorGraph(nodes):
	colors = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]

	queue = []
	for node in nodes:
		if not node in ["eax", "al", "ecx", "edx"]:
			nodes[node].qkey = insertHeap(queue, nodes[node], (nodes[node].unspillable, 0))

	saturate(nodes["eax"],"%eax", nodes, queue)
	saturate(nodes["al"],"%eax", nodes, queue)
	saturate(nodes["ecx"],"%ecx", nodes, queue)
	saturate(nodes["edx"],"%edx", nodes, queue)

	while True:
		next_node = pop(queue)
		"""
		max_saturation = (False, -1)
		for node in nodes:
			if nodes[node].color == None:
				if (nodes[node].unspillable, len(nodes[node].saturation)) > max_saturation:
					max_saturation = (nodes[node].unspillable, len(nodes[node].saturation))
					next_node = node
					"""
		if next_node == None:
			break
		saturate(next_node, color(next_node.saturation, colors), nodes, queue)
	return len(colors) - 6
