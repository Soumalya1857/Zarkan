

from error import *
#######################################
# POSITION
#######################################

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF		= 'EOF'
TT_POW      = 'POW'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD  = 'KEYWORD'
TT_NE 		= 'NE'
TT_LT 		= 'LT'
TT_GT 		= 'GT'
TT_LTE 		= 'LTE'
TT_GTE 		= 'GTE'
TT_EQ		= 'EQ'
TT_EE 		= 'EE' #double equals
TT_COMMA	= 'COMMA'
TT_ARROW	= 'ARROW'




KEYWORDS = [
	'var',
	'and',
	'or',
	'not',
	'if',
	'else',
	'then',
	'elif',
	'for',
	'to',
	'step',
	'while',
	'func'
]

class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

	def matches(self, type_, value):
		return self.type == type_ and self.value == value

#######################################
# NODES
#######################################

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class VarAccessNode:
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case if self.else_case != None else self.cases[len(self.cases)-1][0]).pos_end

class ForNode:
	def __init__(self,var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.body_node.pos_end

class WhileNode:
	def __init__(self,condition_node, body_node):
		self.condition_node = condition_node
		self.body_node = body_node

		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.body_node.pos_end


class FuncDefNode:
	def __init__(self, var_name_tok, arg_name_toks, body_node):
		self.var_name_tok = var_name_tok
		self.arg_name_toks = arg_name_toks
		self.body_node = body_node

		if self.var_name_tok:
			self.pos_start = self.var_name_tok.pos_start
		elif len(self.arg_name_toks) > 0:
			self.pos_start = self.arg_name_toks[0].pos_start
		else:
			self.pos_start = self.body_node.pos_end

class CallNode:
	def __init__(self, node_to_call, arg_nodes):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = self.node_to_call.pos_start
		if len(self.arg_nodes) > 0:
			self.pos_end = self.arg_nodes[len(self.arg_nodes)-1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end


#######################################
# VALUES
#######################################
class Number:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self
	def set_context(self,context = None):
		self.context = context
		return self

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None

	def get_comparison_eq(self,other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).set_context(self.context),None

	def get_comparison_ne(self,other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).set_context(self.context),None

	def get_comparison_lt(self,other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).set_context(self.context),None

	def get_comparison_gt(self,other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).set_context(self.context),None

	def get_comparison_lte(self,other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).set_context(self.context),None

	def get_comparison_gte(self,other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).set_context(self.context),None

	def anded_by(self,other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).set_context(self.context),None

	def ored_by(self,other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).set_context(self.context),None

	def notted(self):
		if isinstance(other,Number):
			return Number(1 if self.value == 0 else 0).set_context(self.context),None


	def is_true(self):
		return self.value != 0

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy	
	def __repr__(self):
		return str(self.value)


######################################
#CONTEXT CLASS
######################################

class Context:
	def __init__(self,display_name,parent=None, parent_entry_pos = None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

############################################
#SYMBOL TABLE CLASS
## KEEPS TRACK OF ALL THE BASIC VAR NAME BOTH LOCAL AND GLOBAL
############################################

class SymbolTable:
	def __init__(self):
		self.symbols = {}
		self.parent = None


	def get(self,name):
		value = self.symbols.get(name,None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self,name):
		del self.symbols[name]



