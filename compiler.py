class Lexer:
    def __init__(self, source_code):
        self.code = source_code
        self.tokens = []

    def tokenize(self):
        lines = self.code.strip().splitlines()
        indent_stack = [0]

        for line in lines:
            if not line.strip():
                continue

            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            if indent > indent_stack[-1]:
                self.tokens.append(('INDENT', None))
                indent_stack.append(indent)
            while indent < indent_stack[-1]:
                self.tokens.append(('DEDENT', None))
                indent_stack.pop()

            for op in ['=', '+', '-', '*', '/', '%', '>', '<']:
                stripped = stripped.replace(op, f' {op} ')

            words = stripped.strip().split()
            for word in words:
                if word.isdigit():
                    self.tokens.append(('NUMBER', int(word)))
                elif word in ('let', 'print', 'if', 'else', 'while', 'for', 'to'):
                    self.tokens.append((word.upper(), word))
                elif word in ('=', '+', '-', '*', '/', '%', '>', '<'):
                    self.tokens.append((word, word))
                elif word.isidentifier():
                    self.tokens.append(('IDENTIFIER', word))
                else:
                    raise SyntaxError(f"Unknown token: {word}")
            self.tokens.append(('EOL', None))

        while len(indent_stack) > 1:
            self.tokens.append(('DEDENT', None))
            indent_stack.pop()

        self.tokens.append(('EOF', None))
        return self.tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return ('EOF', None)

    def consume(self, expected_type=None):
        if self.current >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")
        token = self.tokens[self.current]
        if expected_type and token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token[0]}")
        self.current += 1
        return token

    def match(self, *types):
        if self.current < len(self.tokens) and self.tokens[self.current][0] in types:
            self.current += 1
            return True
        return False

    def parse(self):
        statements = []
        while self.peek()[0] != 'EOF':
            if self.peek()[0] == 'EOL':
                self.consume('EOL')
                continue
            statements.append(self.parse_statement())
        return statements

    def parse_block(self):
        self.consume('INDENT')
        block = []
        while True:
            token = self.peek()[0]
            if token == 'DEDENT':
                break
            if token == 'EOL':
                self.consume('EOL')
                continue
            block.append(self.parse_statement())
        self.consume('DEDENT')
        return block

    def parse_statement(self):
        if self.match('LET'):
            name = self.consume('IDENTIFIER')[1]
            self.consume('=')
            expr = self.parse_expression()
            self.consume('EOL')
            return ('ASSIGN', name, expr)

        if self.peek()[0] == 'IDENTIFIER':
            if self.current + 1 < len(self.tokens) and self.tokens[self.current + 1][0] == '=':
                name = self.consume('IDENTIFIER')[1]
                self.consume('=')
                expr = self.parse_expression()
                self.consume('EOL')
                return ('ASSIGN', name, expr)

        if self.match('PRINT'):
            expr = self.parse_expression()
            self.consume('EOL')
            return ('PRINT', expr)

        if self.match('IF'):
            condition = self.parse_expression()
            self.consume('EOL')
            true_branch = self.parse_block()
            false_branch = []
            if self.match('ELSE'):
                self.consume('EOL')
                false_branch = self.parse_block()
            return ('IF', condition, true_branch, false_branch)

        if self.match('WHILE'):
            condition = self.parse_expression()
            self.consume('EOL')
            body = self.parse_block()
            return ('WHILE', condition, body)

        if self.match('FOR'):
            var = self.consume('IDENTIFIER')[1]
            self.consume('=')
            start = self.parse_expression()
            self.consume('TO')
            end = self.parse_expression()
            self.consume('EOL')
            body = self.parse_block()
            return ('FOR', var, start, end, body)

        raise SyntaxError(f"Unknown statement at token {self.peek()}")


    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        expr = self.parse_term()
        while self.peek()[0] in ('>', '<'):
            op = self.consume()[0]
            right = self.parse_term()
            expr = (op, expr, right)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.peek()[0] in ('+', '-'):
            op = self.consume()[0]
            right = self.parse_factor()
            expr = (op, expr, right)
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.peek()[0] in ('*', '/', '%'):
            op = self.consume()[0]
            right = self.parse_unary()
            expr = (op, expr, right)
        return expr

    def parse_unary(self):
        return self.parse_primary()

    def parse_primary(self):
        token = self.consume()
        if token[0] in ('NUMBER', 'IDENTIFIER'):
            return token
        raise SyntaxError(f"Expected number or identifier, got {token[0]}")


class Interpreter:
    def __init__(self, statements):
        self.statements = statements
        self.env = {}

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
            print(self.eval_expr(expr))
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

