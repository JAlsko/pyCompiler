from structs import *

def newLabel(labels, func):
	ret = func + "_label_" + str(len(labels))
	labels.append(ret)
	return ret

def pair(first, second):
	first.next = second
	second.prev = first
	#print first
	#print second

def ifFlatten(x86IR, labels, func):
	working = x86IR
	while working != None:
		if working.operation == "IfExp":
			label1 = newLabel(labels, func)
			label2 = newLabel(labels, func)
			compareNode = x86IRNode("cmpl", 0, working.var1)
			pair(working.prev, compareNode)
			jump1 = x86IRNode("je", label1, None)
			pair(compareNode, jump1)
			then_ = ifFlatten(working.thenNext, labels, func)
			pair(jump1, then_)
			last = getLast(then_)
			jump2 = x86IRNode("jmp", label2, None)
			pair(last, jump2)
			labelInst = x86IRNode(label1 + ":", None, None)
			pair(jump2, labelInst)
			else_ = ifFlatten(working.elseNext, labels, func)
			pair(labelInst, else_)
			last2 = getLast(else_)
			labelInst2 = x86IRNode(label2 + ":", None, None)
			pair(last2,labelInst2)
			if working.next != None:
				pair(labelInst2,working.next)
		working = working.next
	return x86IR

