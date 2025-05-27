from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QSplitter
)
from PySide6.QtCore import Qt
import sys
from io import StringIO
import contextlib

from compiler import Lexer,Parser,Interpreter
class Interpreter:
    def __init__(self, statements, output_widget=None):
        self.statements = statements
        self.env = {}
        self.output_widget = output_widget

    def print_output(self, value):
        if self.output_widget:
            self.output_widget.append(str(value))
        else:
            print(value)

    def eval_expr(self, expr):
        if isinstance(expr, tuple) and expr[0] in ('+', '-', '*', '/', '%', '>', '<'):
            op, left, right = expr
            lval = self.eval_expr(left)
            rval = self.eval_expr(right)
            if op == '+': return lval + rval
            if op == '-': return lval - rval
            if op == '*': return lval * rval
            if op == '/': return lval // rval if rval != 0 else 0
            if op == '%': return lval % rval if rval != 0 else 0
            if op == '>': return lval > rval
            if op == '<': return lval < rval
        elif expr[0] == 'NUMBER':
            return expr[1]
        elif expr[0] == 'IDENTIFIER':
            var = expr[1]
            if var in self.env:
                return self.env[var]
            else:
                raise NameError(f"Undefined variable '{var}'")
        else:
            return expr

    def exec(self):
        self.execute_statements(self.statements)

    def execute_statements(self, statements):
        for stmt in statements:
            self.execute(stmt)

    def execute(self, stmt):
        if stmt[0] == 'ASSIGN':
            _, name, expr = stmt
            self.env[name] = self.eval_expr(expr)
        elif stmt[0] == 'PRINT':
            _, expr = stmt
            self.print_output(self.eval_expr(expr))
        elif stmt[0] == 'IF':
            _, cond, true_branch, false_branch = stmt
            if self.eval_expr(cond):
                self.execute_statements(true_branch)
            else:
                self.execute_statements(false_branch)
        elif stmt[0] == 'WHILE':
            _, cond, body = stmt
            while self.eval_expr(cond):
                self.execute_statements(body)
        elif stmt[0] == 'FOR':
            _, var, start_expr, end_expr, body = stmt
            start = self.eval_expr(start_expr)
            end = self.eval_expr(end_expr)
            for i in range(start, end + 1):
                self.env[var] = i
                self.execute_statements(body)


def run_compiler(source_code, output_widget=None):
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast, output_widget)
    interpreter.exec()

class CompilerGUI(QWidget):
    def __init__(self):
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_code)

        example_code = """\

"""
        self.code_editor.setText(example_code)

    def run_code(self):
        self.output_console.clear()
        code = self.code_editor.toPlainText()
        try:
            run_compiler(code, self.output_console)
        except Exception as e:
            self.output_console.append(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompilerGUI()
    window.show()
    sys.exit(app.exec())
