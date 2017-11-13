#!/usr/bin/python

import sys
import compiler
from compiler.ast import *
import src.structs as structs
import src.eStructs as eStructs
import src.flatten as flatten
import src.parse as parse
import src.flatPyToX86IR as tox86IR
import src.liveness as liveness
import src.graph as graph
import src.spill as spill
import src.printAssembly as printAssem
import src.explicate as explicate
import src.typeCheck as typeCheck
import src.ifFlatten as ifFlat
import src.uniquify as uniq
import src.heapify as heapify
import src.closure as close
import src.declassify as declass
import src.string as string
import pprint

def main():
	with open(sys.argv[1], "r") as inputFile:
		program = inputFile.read()
		if '-concsyn' in sys.argv or '-all' in sys.argv:
			print program
		inputFile.close()
		#ast = parse.parse(program)
		ast = compiler.parse(program)
		if '-ast' in sys.argv or '-all' in sys.argv:
			print "---------------ast---------------"
			if '-longast' in sys.argv:
				print structs.astReadable(ast)
			else:
				print ast
		declassAst = declass.declassify(ast)
		if '-declassast' in sys.argv or '-all' in sys.argv:
			print "-----------declassAst------------"
			if '-longast' in sys.argv:
				print structs.astReadable(declassAst)
			else:
				print declassAst
		uniqAst = uniq.uniquifyWrapper(declassAst)
		if '-uniqast' in sys.argv or '-all' in sys.argv:	
			print "-------------uniqAst-------------"
			if '-longast' in sys.argv:
				print structs.astReadable(uniqAst)
			else:
				print uniqAst
		explicateAst = explicate.explicate(uniqAst, [])
		if '-explicate' in sys.argv or '-all' in sys.argv:
			print "----------explicateAst-----------"
			if '-longast' in sys.argv:
				print structs.astReadable(explicateAst)
			else:
				print explicateAst
		heapVars = heapify.determineHeapify(explicateAst)
		if '-heapvars' in sys.argv or '-all' in sys.argv:
			print "------------heapVars-------------"
			print heapVars
		heapifiedAst = heapify.heapify(explicateAst, heapVars)
		if '-heapast' in sys.argv or '-all' in sys.argv:
			print "-------------heapAst-------------"
			if '-longast' in sys.argv:
				print structs.astReadable(heapifiedAst)
			else:
				print heapifiedAst
		strings = {}
		noStringAst = string.rmString(heapifiedAst, strings)
		if '-strings' in sys.argv or '-all' in sys.argv:
			print structs.dictToStr(strings)
		if '-stringAst' in sys.argv or '-all' in sys.argv:
			print "------------stringAst------------"
			if '-longast' in sys.argv:
				print structs.astReadable(noStringAst)
			else:
				print structs.dictToStr(noStringAst)
		functions = close.closureWrapper(noStringAst)
		if '-closure' in sys.argv or '-all' in sys.argv:
			print "------------functions------------"
			if '-longast' in sys.argv:
				print structs.astReadable(functions)
			else:
				print structs.dictToStr(functions)
		funcAssem = {}
		nodeGraph = {}
		numColors = {}
		for func in functions:
			#typeCheck.typeCheck(explicateAst, {})
			#print "----------------------------" + func + "----------------------------"
			flatAst, variables = flatten.flatten(functions[func])
			if '-varmap' in sys.argv or '-all' in sys.argv:
				print func + ":--------------varmap-------------"
				print structs.dictToStr(variables)
			if '-flatpy' in sys.argv or '-all' in sys.argv:
				print func + ":------------flatPy--------------"
				structs.printLLwithIf(flatAst, 0)
			flatAssem = tox86IR.createAssembly(flatAst, func)
			if '-flatassem' in sys.argv or '-all' in sys.argv:
				print func + ":------------flatAssem------------"
				structs.printLLwithIf(flatAssem, 0)
			if '-vars' in sys.argv or '-all' in sys.argv:
				print func + ":--------------vars---------------"
				print structs.setToStr(variables)
			liveness.setLiveness(flatAssem, set([]))
			unspillable = []
			while True:
				liveness.setLiveness(flatAssem, set([]))
				if '-liveness' in sys.argv or '-all' in sys.argv:
					print func + ":------------liveness-------------"
					structs.printLLwithIf(flatAssem, 0)
				nodeGraph[func] = graph.createGraphWrapper(flatAssem, variables, unspillable)
				if '-graph' in sys.argv or '-all' in sys.argv:
					print func + ":--------------graph--------------"
					print structs.dictToStr(nodeGraph)
				numColors[func] = graph.colorGraph(nodeGraph[func])
				if '-colors' in sys.argv or '-all' in sys.argv:
					print func + ":-------------colors--------------"
					print structs.dictToStr(nodeGraph)
				(flatAssem, new_unspillable) = spill.checkSpills(flatAssem, nodeGraph[func], variables)
				if '-spills' in sys.argv or '-all' in sys.argv:
					print func + ":-------------spills--------------"
					print structs.setToStr(new_unspillable)
				if not new_unspillable:
					break;
				unspillable.extend(new_unspillable)
			finalFlatAssem = ifFlat.ifFlatten(flatAssem, [], func)
			if '-ifFlat' in sys.argv or '-all' in sys.argv:
				print func + ":-------------ifFlat--------------"
				print structs.printLinkedList(finalFlatAssem)
			funcAssem[func] = finalFlatAssem
		printAssem.createAssembly(sys.argv[1][:-2] + "s", funcAssem, nodeGraph, numColors)

		
main()


