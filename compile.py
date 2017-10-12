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
		explicateAst = explicate.explicate(ast, {})
		if '-explicate' in sys.argv:
			print explicateAst
		typeCheck.typeCheck(explicateAst, {})
		'''
		flatAst, variables = flatten.flatten(ast)
		if '-flatpy' in sys.argv:
			structs.printLinkedList(flatAst)
		flatAssem = tox86IR.createAssembly(flatAst)
		if '-flatassem' in sys.argv:
			structs.printLinkedList(flatAssem)
		if '-vars' in sys.argv:
			print structs.setToStr(variables)
		unspillable = []
		while True:
			liveness.setLiveness(flatAssem)
			if '-liveness' in sys.argv:
				structs.printLinkedList(flatAssem)
			nodeGraph = graph.createGraph(flatAssem, variables, unspillable)
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
		printAssem.createAssembly(sys.argv[1][:-2] + "s", flatAssem, nodeGraph, numColors)
		'''

		
main()
