#!/usr/bin/python

import sys
import src.structs as structs
import src.flatten as flatten
import src.parse as parse
import src.flatPyToX86IR as tox86IR
import src.liveness as liveness

def main():
	with open(sys.argv[1], "r") as inputFile:
		program = inputFile.read()
		if '-concsyn' in sys.argv:
			print program
		inputFile.close()
		ast = parse.parse(program)
		#ast = compile.parse(program)
		if '-ast' in sys.argv:
			print ast
		flatAst = flatten.flatten(ast)
		if '-flatpy' in sys.argv:
			structs.printLinkedList(flatAst)
		flatAssem = tox86IR.createAssembly(flatAst)
		if '-flatassem' in sys.argv:
			structs.printLinkedList(flatAssem)
		liveness.setLiveness(flatAssem)
		if '-liveness' in sys.argv:
			structs.printLinkedList(flatAssem)
		
main()
