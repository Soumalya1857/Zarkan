
from classes import *
from parser import *
from lexer import *
from error import *
import os
import math


######################################
#FUNCTION CLASS
#CLASSES THAT INHERITS VALUE CLASS
######################################

class BaseFunction(Value):
	def __init__(self,name):
		super().__init__()
		self.name = name or "<anonymous>"

	def generate_new_context(self):
		new_context = Context(self.name, self.context, self.pos_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
		return new_context

	def check_args(self, arg_names, args):
		res  = RTResult()

		if len(args) > len(arg_names):
			return res.faliure(RTError(
				self.pos_start, self.pos_end,
				f"{len(args)-len(arg_names)} too many args passed into '{self.name}'",
				self.context
			))

		if len(args) < len(arg_names):
			return res.faliure(RTError(
				self.pos_start, self.pos_end,
				f"{len(arg_names)-len(args)} too few args passed into '{self.name}'",
				self.context
			))

		return res.success(None)

	def populate_args(self, arg_names, args, exec_cntx):
		for i in range(len(args)):
			arg_name = arg_names[i]
			arg_value = args[i]
			arg_value.set_context(exec_cntx)
			exec_cntx.symbol_table.set(arg_name, arg_value)

	def check_and_populate_args(self, arg_names, args, exec_cntx):
		res = RTResult()
		res.register(self.check_args(arg_names, args))
		if res.error: return res
		self.populate_args(arg_names, args, exec_cntx)
		return res.success(None)



class Function(BaseFunction):
	def __init__(self, name, body_node, arg_names, should_return_null):
		super().__init__(name)
		#self.name = name or "<anonymous>"
		self.body_node = body_node
		self.arg_names = arg_names
		self.should_return_null = should_return_null

	def execute(self,args):
		# res = RTResult()
		# interpreter = Interpreter()
		# new_context = Context(self.name, self.context, self.pos_start)

		res = RTResult()
		interpreter = Interpreter()
		exec_cntx = self.generate_new_context()

		res.register(self.check_and_populate_args(self.arg_names, args, exec_cntx))
		if res.error: return res

		value = res.register(interpreter.visit(self.body_node, exec_cntx))
		if res.error: return res
		return res.success(Number.null if self.should_return_null else value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
	def __init__(self, name):
	 super().__init__(name)

	def execute(self, args):
		res = RTResult()
		exec_cntx = self.generate_new_context()

		method_name = f'execute_{self.name}'	
		method = getattr(self, method_name, self.no_visit_method)	

		res.register(self.check_and_populate_args(method.arg_names, args, exec_cntx))
		if res.error: return res

		return_value = res.register(method(exec_cntx))
		if res.error: return res
		return res.success(return_value)


	def no_visit_method(self, node, context):
		raise Exception(f'No execute_{self.name} method defined')

	def copy(self):
		copy = BuiltInFunction(self.name)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f'<built-in function {self.name}>'

	###########################################################
	#THE BUILT-IN-FUNCTIONS DEFINED HERE
	###########################################################

	def execute_print(self, exec_cntx):
		print(str(exec_cntx.symbol_table.get("value")))
		return RTResult().success(Number.null)
	execute_print.arg_names = ['value']

	def execute_print_ret(self, exec_cntx):
		return RTResult().success(String(str(exec_cntx.symbol_table.get("value"))))
		return RTResult().success(Number.null)
	execute_print_ret.arg_names = ['value']

	def execute_input(self, exec_cntx):
		text = input()
		return RTResult().success(String(text))
	execute_input.arg_names = []

	def execute_input_int(self, exec_cntx):
		while True:
			text = input()
			try:
				number = int(text)
				break
			except ValueError:
				print(f"'{text}' must be an integer.Try again!")
		return RTResult().success(Number(number))
	execute_input.arg_names = []

	def execute_clear(self,exec_cntx):
		os.system('cls' if os.name == 'nt' else 'clear')
		return RTResult().success(Number.null)
	execute_clear.arg_names = []

	def execute_is_number(self, exec_cntx):
		is_number = isinstance(exec_cntx.symbol_table.get("value"), Number)
		return RTResult().success(Number.true if is_number else Number.false)
	execute_is_number.arg_names = ['value']

	def execute_is_string(self, exec_cntx):
		is_string = isinstance(exec_cntx.symbol_table.get("value"), String)
		return RTResult().success(Number.true if is_string else Number.false)
	execute_is_string.arg_names = ['value']

	def execute_is_list(self, exec_cntx):
		is_list = isinstance(exec_cntx.symbol_table.get("value"), List)
		return RTResult().success(Number.true if is_list else Number.false)
	execute_is_list.arg_names = ['value']

	def execute_is_function(self, exec_cntx):
		is_basefunction = isinstance(exec_cntx.symbol_table.get("value"), BaseFunction)
		return RTResult().success(Number.true if is_basefunction else Number.false)
	execute_is_function.arg_names = ['value']


	def execute_append(self, exec_cntx):
		list_ = exec_cntx.symbol_table.get("list")
		value = exec_cntx.symbol_table.get("value")

		if not isinstance(list_, List):
			return RTResult().faliure(RTError(
				self.pos_start, self.pos_end,
				"First argumet must be of type list",
				exec_cntx
			))

		list_.elements.append(value)
		return RTResult().success(Number.null)

	execute_append.arg_names = ['list', 'value']


	def execute_pop(self, exec_cntx):
		list_ = exec_cntx.symbol_table.get("list")
		index = exec_cntx.symbol_table.get("index")

		if not isinstance(list_, List):
			return RTResult().faliure(RTError(
				self.pos_start, self.pos_end,
				"First argumet must be of type list",
				exec_cntx
			))

		if not isinstance(index, Number):
			return RTResult().faliure(RTError(
				self.pos_start, self.pos_end,
				"Second argumet must be a number",
				exec_cntx
			))
		try:
			element = list_.elements.pop(index.value)
		except:
			return RTResult().faliure(RTError(
				self.pos_start, self.pos_end,
				"Elements at this index can't be deleted or removed from list because index is out of bound!"
				, exec_cntx
			))

		return RTResult().success(element)

	execute_pop.arg_names = ['list','index']

	def execute_extend(self, exec_cntx):
		list_A = exec_cntx.symbol_table.get("listA")
		list_B= exec_cntx.symbol_table.get("listB")

		if not isinstance(list_A, List):
			return RTResult().faliure(RTError(
				self.pos_start, self.pos_end,
				"First argumet must be of type list",
				exec_cntx
			))
		if not isinstance(list_B, List):
			return RTResult().faliure(RTError(
				self.pos_start, self.pos_end,
				"Second argumet must be of type list",
				exec_cntx
			))

		list_A.elements.extend(list_B.elements)
		return RTResult().success(Number.null)
	execute_extend.arg_names = ["listA", "listB"]

BuiltInFunction.print 			= BuiltInFunction("print")
BuiltInFunction.print_ret 		= BuiltInFunction("print_ret")
BuiltInFunction.input 			= BuiltInFunction("input")
BuiltInFunction.input_int 		= BuiltInFunction("input_int")
BuiltInFunction.clear 			= BuiltInFunction("clear")
BuiltInFunction.is_number 		= BuiltInFunction("is_number")
BuiltInFunction.is_string 		= BuiltInFunction("is_string")
BuiltInFunction.is_list 		= BuiltInFunction("is_list")
BuiltInFunction.is_function 	= BuiltInFunction("is_function")
BuiltInFunction.append 			= BuiltInFunction("append")
BuiltInFunction.pop 			= BuiltInFunction("pop")
BuiltInFunction.extend 			= BuiltInFunction("extend")


###############################################################

class String(Value):
	def __init__(self,value):
		super().__init__()
		self.value = value

	def added_to(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other).set_context(self.context)

	def multed_by(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self,other)

	def is_true(self):
		return len(self.value) > 0

	def copy(self):
		cpy = String(self.value)
		cpy.set_pos(self.pos_start, self.pos_end)
		cpy.set_context(self.context)
		return cpy

	def __repr__(self):
		return f"{self.value}"	


class List(Value):
	def __init__(self, elements):
		super().__init__()
		self.elements = elements

	def added_to(self, other):
		new_list = self.copy()
		new_list.elements.append(other)
		return new_list, None

	def subbed_by(self, other):
		if isinstance(self, other):
			new_list = self.copy()
			try:
				new_list.elements.pop(other.value)
				return new_list, None
			except:
				return None, RTError(
					other.pos_start, other.pos_end,
					"Element at this index could not be removed from list because index is out of bound!!",
					self.context
				)
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self,other):
		if isinstance(other, List):
			new_list = self.copy()
			new_list.elements.extend(other.elements)
			return new_list, None
		else:
			return None, Value.illegal_operation(self, other)

	def dived_by(self, other):
		if isinstance(self, other):
			new_list = self.copy()
			try:
				new_list.elements[other.value]
				return new_list, None
			except:
				return None, RTError(
					other.pos_start, other.pos_end,
					"Element at this index could not be retrieved from list because index is out of bound!!",
					self.context
				)
		else:
			return None, Value.illegal_operation(self, other)	

	def copy(self):
		copy = List(self.elements)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	# def __repr__(self):
	#  return f"[{", ".join([str(x) for x in self.elements])}]"

	def __repr__(self):
		return f'[{", ".join([str(x) for x in self.elements])}]'

#######################################
# INTERPRETER
#######################################

class Interpreter:
	def visit(self, node,context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node,context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	###################################

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_StringNode(self, node, context):
		return RTResult().success(
			String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_VarAccessNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)

		if not value:
			return res.faliure(RTError(
				node.pos_start, node.pos_end,
				f'{var_name} is not defined',
				context
			))

		value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

		return res.success(value)


	def visit_VarAssignNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node,context))
		if res.error: return res

		context.symbol_table.set(var_name, value)
		return res.success(value)

	def visit_BinOpNode(self, node,context):
		res = RTResult()
		left = res.register(self.visit(node.left_node,context))
		if res.error: return res
		right = res.register(self.visit(node.right_node,context))
		if res.error: return res

		if node.op_tok.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == TT_DIV:
			result,error = left.dived_by(right)
		elif node.op_tok.type == TT_POW:
			result, error = left.powed_by(right)
		elif node.op_tok.type == TT_EE:
			result,error = left.get_comparison_eq(right)
		elif node.op_tok.type == TT_NE:
			result,error = left.get_comparison_ne(right)
		elif node.op_tok.type == TT_LT:
			result,error = left.get_comparison_lt(right)
		elif node.op_tok.type == TT_GT:
			result,error = left.get_comparison_gt(right)
		elif node.op_tok.type == TT_GTE:
			result,error = left.get_comparison_gte(right)
		elif node.op_tok.type == TT_LTE:
			result,error = left.get_comparison_lte(right)
		elif node.op_tok.matches(TT_KEYWORD, 'and'):
			result,error = left.anded_by(right)
		elif node.op_tok.matches(TT_KEYWORD, 'or'):
			result,error = left.ored_by(right)
		

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node,context):
		res = RTResult()
		number = res.register(self.visit(node.node,context))
		if res.error: return res

		error = None

		if node.op_tok.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))
		elif node.op_tok.matches(TT_KEYWORD, "not"):
			number, error = number.notted()
			
		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))



	def visit_IfNode(self, node, context):
		res = RTResult()

		for condition, expr, should_return_null  in node.cases:
			conditon_value = res.register(self.visit(condition, context))
			if res.error: return res
			
			if conditon_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.error: return res
				return res.success(Number.null if should_return_null else expr_value)


		if node.else_case:
			expr, should_return_null = node.else_case
			else_value = res.register(self.visit(expr, context))
			if res.error: return res
			return res.success(Number.null if should_return_null else else_value)

		return res.success(Number.null)#for no else cases


	def visit_ForNode(self, node, context):
		res = RTResult()
		elements = []

		start_value = res.register(self.visit(node.start_value_node, context))
		if res.error: return res

		end_value = res.register(self.visit(node.end_value_node, context))
		if res.error: return res
		
		if node.step_value_node:
			step_value = res.register(self.visit(node.step_value_node, context))
			if res.error: return res
		else: 
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value
		else:
			condition = lambda: i > end_value.value

		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i))
			i += step_value.value

			elements.append(res.register(self.visit(node.body_node, context)))
			if res.error: return res

		return res.success(
			Number.null if node.should_return_null else 
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_WhileNode(self, node, context):
		res = RTResult()
		elements = []

		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.error: return res

			if not condition.is_true(): break

			elements.append(res.register(self.visit(node.body_node, context)))
			if res.error: return res

		return res.success(
			Number.null if node.should_return_null else
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)



	def visit_FuncDefNode(self, node, context):
		res = RTResult()

		func_name = node.var_name_tok.value if node.var_name_tok else None
		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks]
		func_value = Function(func_name, body_node, arg_names, node.should_return_null).set_context(context).set_pos(node.pos_start, node.pos_end)

		if node.var_name_tok:
			context.symbol_table.set(func_name, func_value)

		return res.success(func_value)


	def visit_CallNode(self, node, context):
		res = RTResult()
		args = [] 

		value_to_call = res.register(self.visit(node.node_to_call, context))
		if res.error: return res
		value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node, context)))
			if res.error: return res

		return_value = res.register(value_to_call.execute(args))
		if res.error: return res
		return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		return res.success(return_value)


	def visit_ListNode(self, node, context):
		res = RTResult()
		elements = []

		for element_node in node.element_nodes:
			elements.append(res.register(self.visit(element_node, context)))
			if res.error: return res

		return res.success(
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)



#######################################
# RUN
#######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("null",Number.null)
global_symbol_table.set("NULL",Number.null)
global_symbol_table.set("TRUE",Number.true)
global_symbol_table.set("FALSE",Number.false)
global_symbol_table.set("true",Number.true)
global_symbol_table.set("false",Number.false)

global_symbol_table.set("math_pi", Number.math_pi)
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_num", BuiltInFunction.is_number)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_func", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)


def run(fn, text):
	# Generate tokens
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()
	if error: return None, error
	
	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	# Run program

	interpreter = Interpreter()
	context = Context("<program>")
	context.symbol_table = global_symbol_table
	result = interpreter.visit(ast.node,context)

	return result.value, result.error
