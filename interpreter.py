# Walks the AST and executes the program.
# Uses the visitor pattern to evaluate expressions and run statements.
import time

from expr import (
    ExprVisitor,
    Binary,
    Grouping,
    Literal,
    Unary,
    Variable,
    Assign,
    Logical,
    Call,
    Get,
    Set,
    This,
    Super,
)
from stmt import (
    StmtVisitor,
    Expression,
    Print,
    Var,
    Block,
    If,
    While,
    Function,
    Return,
    Class,
)
from token_type import TokenType
from environment import Environment
from lox_callable import LoxCallable
from lox_function import LoxFunction
from lox_class import LoxClass
from lox_instance import LoxInstance
from return_exception import ReturnException


class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token


class ClockCallable(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments):
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

        self.globals.define("clock", ClockCallable())

    def interpret(self, statements):
        from lox import Lox

        if Lox.had_error:
            return

        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            Lox.runtime_error(error)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_expression_stmt(self, stmt: Expression):
        self.evaluate(stmt.expression)
        return None

    def visit_print_stmt(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_block_stmt(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt: Class):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(
                method,
                self.environment,
                method.name.lexeme == "init",
                )
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)
        return None

    def visit_if_stmt(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_while_stmt(self, stmt: While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visit_function_stmt(self, stmt: Function):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_return_stmt(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise ReturnException(value)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)

        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)

        return None

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        t = expr.operator.type

        if t == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)

        if t == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)

        if t == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        if t == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")

        if t == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)

        if t == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)

        if t == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)

        if t == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)

        if t == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        if t == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        return None

    def visit_variable_expr(self, expr: Variable):
        return self.look_up_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_logical_expr(self, expr: Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_call_expr(self, expr: Call):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")

        function = callee
        if len(arguments) != function.arity():
            raise RuntimeError(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )

        return function.call(self, arguments)

    def visit_get_expr(self, expr: Get):
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RuntimeError(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr: Set):
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_this_expr(self, expr: This):
        return self.look_up_variable(expr.keyword, expr)

    def visit_super_expr(self, expr: Super):
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(distance, "super")

        obj = self.environment.get_at(distance - 1, "this")

        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")

        return method.bind(obj)

    def look_up_variable(self, name, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def is_equal(self, a, b):
        return a == b

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    def stringify(self, value):
        if value is None:
            return "nil"

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(value)