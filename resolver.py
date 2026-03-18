from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve(self, thing):
        if isinstance(thing, list):
            for statement in thing:
                self.resolve(statement)
        else:
            thing.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            from lox import Lox
            Lox.token_error(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def define(self, name):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolve_function(self, function, function_type):
        enclosing_function = self.current_function
        self.current_function = function_type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def visit_class_stmt(self, stmt):
        from lox import Lox

        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            Lox.token_error(stmt.superclass.name, "A class can't inherit from itself.")

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass is not None:
            self.end_scope()

        self.current_class = enclosing_class
        return None

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
        return None

    def visit_variable_expr(self, expr):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            from lox import Lox
            Lox.token_error(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)
        return None

    def visit_assign_expr(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def visit_expression_stmt(self, stmt):
        self.resolve(stmt.expression)
        return None

    def visit_if_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt):
        self.resolve(stmt.expression)
        return None

    def visit_return_stmt(self, stmt):
        from lox import Lox

        if self.current_function == FunctionType.NONE:
            Lox.token_error(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                Lox.token_error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)

        return None

    def visit_while_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visit_binary_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_call_expr(self, expr):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
        return None

    def visit_get_expr(self, expr):
        self.resolve(expr.object)
        return None

    def visit_grouping_expr(self, expr):
        self.resolve(expr.expression)
        return None

    def visit_literal_expr(self, expr):
        return None

    def visit_logical_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_set_expr(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None

    def visit_super_expr(self, expr):
        from lox import Lox

        if self.current_class == ClassType.NONE:
            Lox.token_error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            Lox.token_error(expr.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)
        return None

    def visit_this_expr(self, expr):
        from lox import Lox

        if self.current_class == ClassType.NONE:
            Lox.token_error(expr.keyword, "Can't use 'this' outside of a class.")
            return None

        self.resolve_local(expr, expr.keyword)
        return None

    def visit_unary_expr(self, expr):
        self.resolve(expr.right)
        return None