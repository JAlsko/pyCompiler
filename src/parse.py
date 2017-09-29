import compiler
from compiler.ast import *
import ply.lex as lex
import ply.yacc as yacc


def parse(input):
	reserved = {'print' : 'PRINT', 'input' : 'INPUT'}
	tokens = ['INT','PLUS','ASSIGN','PAREN_START','PAREN_END','NEG','NAME','NEW_LINE'] + list(reserved.values())
	t_PRINT = r'print'
	t_PLUS = r'\+'
	t_NEG = r'\-'
	t_ASSIGN = r'='
	t_INPUT = r'input'
	t_PAREN_START = r'\('
	t_PAREN_END = r'\)'
	t_NEW_LINE = r'\n'
	#t_VAR = r'[a-zA-Z_][a-zA-Z0-9_]*'
	def t_NAME(t):
		r'[a-zA-Z_][a-zA-Z_0-9]*'
		t.type = reserved.get(t.value,'NAME')
		return t
	def t_INT(t):
		r'\d+'
		try:
			t.value = int(t.value)
		except ValueError:
			print "integer value too large", t.value
			t.value = 0
		return t
	def t_COMMENT(t):
		r'\#.*'
		pass
	t_ignore  = ' \t'
	'''
	def t_newline(t):
		r'\n+'
		t.lexer.lineno += t.value.count("\n")
	'''
	def t_error(t):
		print "Illegal character '%s'" % t.value[0]
		t.lexer.skip(1)
	myLexer = lex.lex()
	myLexer.input(input)
	#for token in myLexer:
	#	print token
	#Parser
	from compiler.ast import Printnl, Add, Const, UnarySub, Name, Assign, AssName, CallFunc
	precedence = (
		('nonassoc','PRINT'),
		('left','PLUS', 'NEG')
		)
	def p_module_module(t):
		'module : statement_list'
		t[0] = Module(None, Stmt(t[1]))
	def p_newline_statement(t):
		'statement_list : statement_list NEW_LINE statement'
		t[0] = t[1]
		t[0].append(t[3])
	def p_statement_list(t):
		'statement_list : statement'
		t[0] = [t[1]]
	def p_empty_statement(t):
		'statement : '
	def p_print_statement(t):
		'statement : PRINT expression'
		t[0] = Printnl([t[2]], None)
	def p_assign_statement(t):
		'statement : NAME ASSIGN expression'
		t[0] = Assign([AssName(t[1], 'OP_ASSIGN')], t[3])
	def p_disard_statement(t):
		'statement : expression'
		t[0] = Discard(t[1])
	def p_plus_expression(t):
		'expression : expression PLUS expression'
		t[0] = Add((t[1], t[3]))
	def p_neg_expression(t):
		'expression : NEG expression'
		t[0] = UnarySub(t[2])
	def p_int_expression(t):
		'expression : INT'
		t[0] = Const(t[1])
	def p_name_expression(t):
		'expression : NAME'
		t[0] = Name(t[1])
	def p_paren_expression(t):
		'expression : PAREN_START expression PAREN_END'
		t[0] = t[2]
	def p_input_expression(t):
		'expression : INPUT PAREN_START PAREN_END'
		t[0] = CallFunc(Name('input'), [], None, None)
	def p_error(t):
		print "Syntax error at '%s'" % t.value
	parser = yacc.yacc()
	return parser.parse(lexer=myLexer)
