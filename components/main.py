from analyzer.lexer import *
from analyzer.parser import *
from analyzer.tokenizer import *
from components.context import *
from components.runtime_result import *
from components.list import *
from components.error import *
from components.error_position import *
from components.string import *
from components.number import *
from components.token_type import *
from components.constant import *
from components.string import *
from components.arrow_function import *
from components.node import *
from components.variable import *
from components.base_function import *
from components.symbol_table import *

import os


######################
# FUNCTION
######################


class Function(BaseFunction):
  def __init__(self, name, body_node, arg_names, should_auto_return):
    super().__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_auto_return = should_auto_return

  def execute(self, args):
    res = RunTimeResult()
    interpreter = Interpreter()
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_return_value == None: return res

    ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
    return res.success(ret_value)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = RunTimeResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)
  
  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"

  def execute_show(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return RunTimeResult().success(Number.null)
  execute_show.arg_names = ['value']
  
  def execute_return_function(self, exec_ctx):
    return RunTimeResult().success(String(str(exec_ctx.symbol_table.get('value'))))
  execute_return_function.arg_names = ['value']
  
  def execute_input(self, exec_ctx):
    text = input()
    return RunTimeResult().success(String(text))
  execute_input.arg_names = []

  def execute_int_input(self, exec_ctx):
    while True:
      text = input()
      try:
        number = int(text)
        break
      except ValueError:
        print(f"'{text}' must be an integer.")
    return RunTimeResult().success(Number(number))
  execute_int_input.arg_names = []

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'clear') 
    return RunTimeResult().success(Number.null)
  execute_clear.arg_names = []

  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_function.arg_names = ["value"]

  def execute_insert(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    value = exec_ctx.symbol_table.get("value")

    if not isinstance(List_, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "First argument must be list.",
        exec_ctx
      ))

    list_.elements.append(value)
    return RunTimeResult().success(Number.null)
  execute_insert.arg_names = ["list", "value"]

  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "First argument must be list.",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Second argument must be number.",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds.',
        exec_ctx
      ))
    return RunTimeResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_ctx):
    list_A = exec_ctx.symbol_table.get("list_A")
    list_B = exec_ctx.symbol_table.get("list_B")

    if not isinstance(list_A, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "First argument must be list.",
        exec_ctx
      ))

    if not isinstance(list_B, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Second argument must be list.",
        exec_ctx
      ))

    list_A.elements.extend(list_B.elements)
    return RunTimeResult().success(Number.null)
  execute_extend.arg_names = ["list_A", "list_B"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Argument must be list.",
        exec_ctx
      ))

    return RunTimeResult().success(Number(len(list_.elements)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Second argument must be string.",
        exec_ctx
      ))

    fn = fn.value

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)
    
    if error:
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))

    return RunTimeResult().success(Number.null)
  execute_run.arg_names = ["fn"]

BuiltInFunction.print             = BuiltInFunction("show")
BuiltInFunction.return_function   = BuiltInFunction("return_function")
BuiltInFunction.input             = BuiltInFunction("input")
BuiltInFunction.int_input         = BuiltInFunction("int_input")
BuiltInFunction.clear             = BuiltInFunction("clear")
BuiltInFunction.is_number         = BuiltInFunction("is_number")
BuiltInFunction.is_string         = BuiltInFunction("is_string")
BuiltInFunction.is_list          = BuiltInFunction("is_list")
BuiltInFunction.is_function       = BuiltInFunction("is_function")
BuiltInFunction.insert            = BuiltInFunction("insert")
BuiltInFunction.pop               = BuiltInFunction("pop")
BuiltInFunction.extend            = BuiltInFunction("extend")
BuiltInFunction.len					      = BuiltInFunction("len")
BuiltInFunction.run					      = BuiltInFunction("run")




##############
# INTERPRETER
##############



class Interpreter:
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')

  def visit_NumberNode(self, node, context):
    return RunTimeResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_StringNode(self, node, context):
    return RunTimeResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ListNode(self, node, context):
    res = RunTimeResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_VarAccessNode(self, node, context):
    res = RunTimeResult()
    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RunTimeError(
        node.pos_start, node.pos_end,
        f"'{var_name}' is not defined.",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  def visit_VarAssignNode(self, node, context):
    res = RunTimeResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinOpNode(self, node, context):
    res = RunTimeResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    if node.op_tok.type == TT_PLUS:
      result, error = left.addition_to(right)
    
    elif node.op_tok.type == TT_MINUS:
      result, error = left.subtract_by(right)
    
    elif node.op_tok.type == TT_MUL:
      result, error = left.multiply_to(right)
    
    elif node.op_tok.type == TT_DIV:
      result, error = left.division_by(right)

    elif node.op_tok.type == TT_INDEX:
      result, error = left.index_at(right)
    
    elif node.op_tok.type == TT_POW:
      result, error = left.power_by(right)

    elif node.op_tok.type == TT_MOD:
      result, error = left.mod_by(right)
    
    elif node.op_tok.type == TT_DOUBLE_EQUAL:
      result, error = left.get_comparison_eq(right)
    
    elif node.op_tok.type == TT_NOT_EQUAL:
      result, error = left.get_comparison_ne(right)
    
    elif node.op_tok.type == TT_LESS_THAN:
      result, error = left.get_comparison_lt(right)
    
    elif node.op_tok.type == TT_GREATER_THAN:
      result, error = left.get_comparison_gt(right)
    
    elif node.op_tok.type == TT_LESS_THAN_EQUAL:
      result, error = left.get_comparison_lte(right)
    
    elif node.op_tok.type == TT_GREATER_THAN_EQUAL:
      result, error = left.get_comparison_gte(right)
    
    elif node.op_tok.matches(TT_KEYWORD, 'and'):
      result, error = left.anded_by(right)
    
    elif node.op_tok.matches(TT_KEYWORD, 'or'):
      result, error = left.ored_by(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  def visit_UnaryOpNode(self, node, context):
    res = RunTimeResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    if node.op_tok.type == TT_MINUS:
      number, error = number.multiply_to(Number(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'not'):
      number, error = number.notted()

    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  def visit_IfNode(self, node, context):
    res = RunTimeResult()

    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Number.null if should_return_null else expr_value)

    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Number.null if should_return_null else expr_value)

    return res.success(Number.null)

  def visit_ForNode(self, node, context):
    res = RunTimeResult()
    elements = []

    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res

    end_value = res.register(self.visit(node.end_value_node, context))
    if res.should_return(): return res

    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
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

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
      
      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_WhileNode(self, node, context):
    res = RunTimeResult()
    elements = []

    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      if not condition.is_true():
        break

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_FuncDefNode(self, node, context):
    res = RunTimeResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
    
    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node, context):
    res = RunTimeResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  def visit_ReturnNode(self, node, context):
    res = RunTimeResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Number.null
    
    return res.success_return(value)

  def visit_ContinueNode(self, node, context):
    return RunTimeResult().success_continue()

  def visit_BreakNode(self, node, context):
    return RunTimeResult().success_break()




#####################
# GLOBAL SYMBOL TABLE
#####################




global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("pi", Number.math_PI)
global_symbol_table.set("show", BuiltInFunction.print)
global_symbol_table.set("return", BuiltInFunction.return_function)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("int_input", BuiltInFunction.int_input)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_num", BuiltInFunction.is_number)
global_symbol_table.set("is_str", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_fun", BuiltInFunction.is_function)
global_symbol_table.set("insert", BuiltInFunction.insert)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)



##############
# RUN PROGRAM
##############



def run(fn, text):
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error
  
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error
