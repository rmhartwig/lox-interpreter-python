# Debug utility that prints AST nodes in a readable format.
# Useful for verifying parser output.
from expr import ExprVisitor, Binary, Grouping, Literal, Unary, Variable, Assign


class AstPrinter(ExprVisitor):
    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        if expr.value is True:
            return "true"
        if expr.value is False:
            return "false"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr: Variable) -> str:
        return expr.name.lexeme

    def visit_assign_expr(self, expr: Assign) -> str:
        return self.parenthesize(f"= {expr.name.lexeme}", expr.value)

    def parenthesize(self, name: str, *exprs) -> str:
        parts = [f"({name}"]
        for expr in exprs:
            parts.append(f" {expr.accept(self)}")
        parts.append(")")
        return "".join(parts)