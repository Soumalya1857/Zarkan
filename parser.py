

from classes import *
from error import *
from lexer import *

#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, ):
		self.tok_idx += 1
		# if self.tok_idx < len(self.tokens):
		# 	self.current_tok = self.tokens[self.tok_idx]
		self.update_current_tok()
		return self.current_tok

	def update_current_tok(self):
		if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]

	def reverse(self, amount = 1):
		self.tok_idx -= amount
		self.update_current_tok()
		return self.current_tok

	def next_token(self):
		if self.tok_idx + 1 < len(self.tokens):
			self.next_tok = self.tokens[self.tok_idx + 1]
		return self.next_tok

	def matches(self, type_, value):
		return self.type == type_ and self.value == value

	def parse(self):
		res = self.statements()
		if not res.error and self.current_tok.type != TT_EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*','/', '^,'==', '!=', '<', '<=', '>', '>=','and' or 'or'"
			))
		return res

	# def if_expr(self):
	# 	res = ParseResult()
	# 	cases = []
	# 	else_case = None

	# 	if not self.current_tok.matches(TT_KEYWORD, 'if'):
	# 		return res.failure(InvalidSyntaxError(
	# 			self.current_tok.pos_start, self.current_tok.pos_end,
	# 			"Expected 'if'"
	# 		))

	# 	res.register_advancement()
	# 	self.advance()

	# 	condition = res.register(self.expr())
	# 	if res.error: return res

	# 	if not self.current_tok.matches(TT_KEYWORD, 'then'):
	# 		return res.faliure(InvalidSyntaxError(
	# 			self.current_tok.pos_start, self.current_tok.pos_end,
	# 			"Expected 'then'"
	# 		))

	# 	res.register_advancement()
	# 	self.advance()

	# 	expr = res.register(self.expr())
	# 	if res.error: return res
	# 	cases.append((condition, expr))#contains all the if conditions

	# 	while self.current_tok.matches(TT_KEYWORD, 'elif'):
	# 		res.register_advancement()
	# 		self.advance()

	# 		condition = res.register(self.expr())
	# 		if res.error: return res

	# 		if not self.current_tok.matches(TT_KEYWORD, 'then'):
	# 			return res.faliure(InvalidSyntaxError(
	# 			self.current_tok.pos_start, self.current_tok.pos_end,
	# 			"Expected 'then'"
	# 		))
	# 		res.register_advancement()
	# 		self.advance()

	# 		expr = res.register(self.expr())
	# 		if res.error: return res
	# 		cases.append((condition, expr))

	# 	if self.current_tok.matches(TT_KEYWORD, 'else'):
	# 		res.register_advancement()
	# 		self.advance()

	# 		else_case = res.register(self.expr())
	# 		if res.error: return res

	# 	return res.success(IfNode(cases, else_case))

	def base_if_expr(self, case_keyword):
		res = ParseResult()
		cases = []
		else_cases = None

		if not self.current_tok.matches(TT_KEYWORD, case_keyword):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
	 			f'Expected {case_keyword}'
			))
		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'then'):
			return res.faliure(InvalidSyntaxError(
	 			self.current_tok.pos_start, self.current_tok.pos_end,
	 			"Expected 'then'"
	 		))
		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			statements = res.register(self.statements())
			if res.error: return res
			cases.append((condition, statements, True))# true for should_return_null variable

			if self.current_tok.matches(TT_KEYWORD, 'end'):
				res.register_advancement()
				self.advance()
			else:
				all_cases = res.register(self.if_expr_else_or_elif())
				if res.error: return res
				new_cases, else_cases = all_cases
				cases.extend(new_cases)	
		else:
			expr = res.register(self.expr())
			if res.error: return res
			cases.append((condition, expr, False))

			all_cases = res.register(self.if_expr_else_of_elif())
			if res.error: return res
			new_cases, else_cases = all_cases
			cases.extend(new_cases)

		return res.success((cases, else_cases))


	def if_expr_elif(self):
		return self.base_if_expr('elif')


	def if_expr_else(self):
		res = ParseResult()
		else_case = None

		if self.current_tok.matches(TT_KEYWORD, 'else'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()

				statements = res.register(self.statements())
				if res.error: return res
				else_case = (statements, True)

				if self.current_tok.matches(TT_KEYWORD, 'end'):
					res.register_advancement()
					self.advance()
				else:
					return res.faliure(InvalidSyntaxError(
	 			self.current_tok.pos_start, self.current_tok.pos_end,
	 			"Expected 'end'"
	 			))
			else:
				expr = res.register(self.expr())
				if res.error: return res
				else_case = (expr, False)
		return res.success(else_case)


	def if_expr_else_of_elif(self):

		res = ParseResult()
		cases, else_cases = [], None

		if self.current_tok.matches(TT_KEYWORD, 'elif'):
			all_cases = res.register(self.if_expr_elif())
			if res.error: return res
			cases, else_cases = all_cases
		else:
			else_cases = res.register(self.if_expr_else())
			if res.error: return res

		return res.success((cases, else_cases))

	def if_expr(self):
		res = ParseResult()
		all_cases = res.register(self.base_if_expr('if'))
		if res.error: return res
		cases, else_cases = all_cases
		return res.success(IfNode(cases, else_cases))


	def for_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'for'):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'then'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_IDENTIFIER:
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected identifier"
			))

		var_name = self.current_tok
		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_EQ:
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '='"
			))

		res.register_advancement()
		self.advance()

		start_value = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'to'):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'to'"
			))

		res.register_advancement()
		self.advance()

		end_value = res.register(self.expr())
		if res.error: return res

		if self.current_tok.matches(TT_KEYWORD, 'step'):
			res.register_advancement()
			self.advance()

			step_value = res.register(self.expr())
			if res.error: return res
		else:
			step_value = None

		if not self.current_tok.matches(TT_KEYWORD, 'then'):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'then'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			body = res.register(self.statements())
			if res.error: return res

			if not self.current_tok.matches(TT_KEYWORD, 'end'):
				return res.faliure(InvalidSyntaxError(
	 			self.current_tok.pos_start, self.current_tok.pos_end,
	 			"Expected 'end'"
	 			)) 
			res.register_advancement()
			self.advance()
			return res.success(ForNode(var_name, start_value, end_value,step_value,body,True))

		body = res.register(self.expr())
		if res.error: return res

		return res.success(ForNode(var_name,start_value,end_value,step_value,body,False))


	def while_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'while'):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'while'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'then'):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'then'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			body = res.register(self.statements())
			if res.error: return res

			if not self.current_tok.matches(TT_KEYWORD, 'end'):
				return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'end'"
				))
			res.register_advancement()
			self.advance()

			return res.success(WhileNode(condition, body, True))


		body = res.register(self.expr())
		if res.error: return res

		return res.success(WhileNode(condition, body, False))


	def func_def(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'func'):
			return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'func'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_IDENTIFIER:
			var_name_tok = self.current_tok
			res.register_advancement()
			self.advance()
			if self.current_tok.type != TT_LPAREN:
				return res.faliure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '('"
				))

		else:
			var_name_tok = None
			if self.current_tok.type != TT_LPAREN:
				return res.faliure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '(' or identifier"
				))

		res.register_advancement()
		self.advance()
		arg_name_toks = []

		if self.current_tok.type == TT_IDENTIFIER:
			arg_name_toks.append(self.current_tok)
			res.register_advancement()
			self.advance()

			while self.current_tok.type == TT_COMMA:
				res.register_advancement()
				self.advance()

				if self.current_tok.type != TT_IDENTIFIER:
					return res.faliure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected identifier"
						))

				arg_name_toks.append(self.current_tok)
				res.register_advancement()
				self.advance()

		
			if self.current_tok.type != TT_RPAREN:
				return res.faliure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ',' or ')'"
					))

		else:

			if self.current_tok.type != TT_RPAREN:
				return res.faliure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected identifier or ')'"
				))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_ARROW:
			# return res.faliure(InvalidSyntaxError(
			# 	self.current_tok.pos_start, self.current_tok.pos_end,
			# 	"Expected '->'"
			# ))

			res.register_advancement()
			self.advance()
			node_to_return = res.register(self.expr())
			if res.error: return res

			return res.success(FuncDefNode(
				var_name_tok, arg_name_toks,node_to_return,False
			))

		if self.current_tok.type != TT_NEWLINE:
			return res.faliure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '->' or NEWLINE "
				))
		res.register_advancement()
		self.advance()

		body = res.register(self.statements())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'end'):
				return res.faliure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'end'"
				))
		res.register_advancement()
		self.advance()

		return res.success(
			FuncDefNode(
				var_name_tok,
				arg_name_toks,
				body,
				True

			)
		)




	def call(self):
		res = ParseResult()
		atom = res.register(self.atom())
		if res.error: return res

		if self.current_tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()

			arg_nodes = []
			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
			else:
				arg_nodes.append(res.register(self.expr()))
				if res.error: 
					return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected 'VAR', int, float, identifier, 'if', 'for', 'while','func','not','+', '-' ,'(', '[' or ')'"
				))

				while self.current_tok.type == TT_COMMA:
					res.register_advancement()
					self.advance()

					arg_nodes.append(res.register(self.expr()))
					if res.error: return res
				
				if self.current_tok.type != TT_RPAREN:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected '',' or ')'"
						))

				res.register_advancement()
				self.advance()

			return res.success(CallNode(atom, arg_nodes))

		return res.success(atom)

	def list_expr(self):
		res = ParseResult()
		element_nodes = []
		pos_start = self.current_tok.pos_start.copy()

		if self.current_tok.type != TT_LSQUARE:
			return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected '['"
						))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_RSQUARE:
			res.register_advancement()
			self.advance()

		else:
			element_nodes.append(res.register(self.expr()))
			if res.error: 
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected 'VAR', int, float, identifier, 'if', 'for', 'while','func','not','+', '-' ,'[' or ']'"
				))

			while self.current_tok.type == TT_COMMA:
				res.register_advancement()
				self.advance()

				element_nodes.append(res.register(self.expr()))
				if res.error: return res
				
			if self.current_tok.type != TT_RSQUARE:
				return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected '',' or ']'"
						))

			res.register_advancement()
			self.advance()

		return res.success(ListNode(
			element_nodes,
			pos_start,
			self.current_tok.pos_end.copy()
	
		))
		

	###################################
	def atom(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_INT, TT_FLOAT):
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == TT_STRING:
			res.register_advancement()
			self.advance()
			return res.success(StringNode(tok))

		elif tok.type == TT_IDENTIFIER:
			res.register_advancement()
			self.advance()
			return res.success(VarAccessNode(tok))

		elif tok.type == TT_LPAREN:
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		elif tok.type == TT_LSQUARE:
			list_expr = res.register(self.list_expr())
			if res.error: return res
			return res.success(list_expr)

		elif tok.matches(TT_KEYWORD, 'if'):
			if_expr = res.register(self.if_expr())
			if res.error: return res
			return res.success(if_expr)

		elif tok.matches(TT_KEYWORD, 'for'):
			for_expr = res.register(self.for_expr())
			if res.error: return res
			return res.success(for_expr)

		elif tok.matches(TT_KEYWORD, 'while'):
			while_expr = res.register(self.while_expr())
			if res.error: return res
			return res.success(while_expr)

		elif tok.matches(TT_KEYWORD, 'func'):
			func_expr = res.register(self.func_def())
			if res.error: return res
			return res.success(func_expr)

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float,identifier, 'if', 'for', 'while', 'func', '+', '-'. '(' or '[' "
		))

		


	def power(self):
		return self.bin_op(self.call, (TT_POW, ), self.factor)


	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		return self.power()
		

	def comp_expr(self):
		res = ParseResult()

		if self.current_tok.matches(TT_KEYWORD, "not"):
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()

			node = res.register(self.comp_expr())
			if res.error: return res
			return res.sucess(UnaryOpNode(op_tok, node))

		#we are looking at second part of the grammer
		node = res.register(self.bin_op(self.arith_expr, (TT_NE,TT_EE,TT_GT,TT_GTE,TT_LT,TT_LTE)))

		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected int or float,identifier, '+', '-' ,'(', '[' or 'not'"
			))

		return res.success(node)

	def arith_expr(self):
		return self.bin_op(self.term, (TT_PLUS,TT_MINUS))

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))


	def expr(self):
		res = ParseResult()

		#this block reassign var values
		if self.current_tok.type == TT_IDENTIFIER and self.next_token().type == TT_EQ:
			var_name = self.current_tok
			res.register_advancement()
			self.advance()
			if self.current_tok.type != TT_EQ:
				return res.faliure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected equals sign"
				))

			res.register_advancement()
			self.advance()
			exp = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(var_name, exp))


		if self.current_tok.matches(TT_KEYWORD, 'var'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected identifier"
				))

			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(var_name, expr))

		# node = res.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS)))
		node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'VAR', int, float, identifier, 'if', 'for', 'while','func','not','+', '-','(' or '['"
			))

		return res.success(node)



	def statements(self):
		res = ParseResult()
		statements = []
		pos_start = self.current_tok.pos_start.copy()

		while self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

		statement = res.register(self.expr())
		if res.error: return res
		statements.append(statement)

		more_statement = True
		while True:
			newline_count = 0
			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()
				newline_count += 1
			if newline_count == 0:
				more_statement = False
			if not more_statement:
				break
			statement = res.try_register(self.expr())
			if not statement:
				self.reverse(res.to_reverse_count)
				more_statement = False
				continue
			statements.append(statement)

		return res.success(
			ListNode(
				statements,
				pos_start,
				self.current_tok.pos_end.copy()
			)
		)

	###################################

	def bin_op(self, func_a, ops, func_b= None):
		if func_b == None:
			func_b = func_a

		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func_b())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)



