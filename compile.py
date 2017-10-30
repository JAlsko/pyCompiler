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
import pprint

def main():
	with open(sys.argv[1], "r") as inputFile:
		program = inputFile.read()
		if '-concsyn' in sys.argv:
			print program
		inputFile.close()
		#ast = parse.parse(program)
		ast = compiler.parse(program)
		if '-ast' in sys.argv:
			print ast
		uniqAst = uniq.uniquifyWrapper(ast)
		if '-uniqast' in sys.argv:
			print uniqAst
		explicateAst = explicate.explicate(uniqAst, {})
		if '-explicate' in sys.argv:
			print explicateAst

		'''
		typeCheck.typeCheck(explicateAst, {})
		flatAst, variables = flatten.flatten(explicateAst)
		if '-flatpy' in sys.argv:
			structs.printLLwithIf(flatAst, 0)
		flatAssem = tox86IR.createAssembly(flatAst)
		if '-flatassem' in sys.argv:
			structs.printLLwithIf(flatAssem, 0)
		if '-vars' in sys.argv:
			print structs.setToStr(variables)
		liveness.setLiveness(flatAssem, set([]))
		unspillable = []
		while True:
			liveness.setLiveness(flatAssem, set([]))
			if '-liveness' in sys.argv:
				structs.printLLwithIf(flatAssem, 0)
			nodeGraph = graph.createGraphWrapper(flatAssem, variables, unspillable)
			if '-graph' in sys.argv:
				print structs.dictToStr(nodeGraph)
			numColors = graph.colorGraph(nodeGraph)
			if '-colors' in sys.argv:
				print structs.dictToStr(nodeGraph)
			(flatAssem, new_unspillable) = spill.checkSpills(flatAssem, nodeGraph, variables)
			if '-spills' in sys.argv:
				print structs.setToStr(new_unspillable)
			if not new_unspillable:
				break;
			unspillable.extend(new_unspillable)
		finalFlatAssem = ifFlat.ifFlatten(flatAssem, [])
		if '-ifFlat' in sys.argv:
			print structs.printLinkedList(finalFlatAssem)
		printAssem.createAssembly(sys.argv[1][:-2] + "s", finalFlatAssem, nodeGraph, numColors)'''

		
main()
