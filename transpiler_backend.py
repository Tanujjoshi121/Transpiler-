def indent(level):
    return ' ' * (4 * level)

def get_indent(line):
    """Return indentation level (4 spaces per indent)."""
    return (len(line) - len(line.lstrip(' '))) // 4

def transpile_to_cpp(source_code):
    lines = source_code.strip('\n').splitlines()
    output = ['#include <iostream>', 'using namespace std;', 'int main() {']
    indent_level = 1
    block_stack = []
    prev_indent = 0

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        current_indent = get_indent(raw_line)
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        if line != "else":
            while block_stack and current_indent < prev_indent:
                indent_level -= 1
                block_stack.pop()
                output.append(f"{indent(indent_level)}}}")
                prev_indent -= 1

        if line.startswith("let "):
            var, val = map(str.strip, line[4:].split('=', 1))
            output.append(f"{indent(indent_level)}int {var} = {val};")
        elif line.startswith("print "):
            output.append(f"{indent(indent_level)}cout << {line[6:].strip()} << endl;")
        elif line.startswith("if "):
            output.append(f"{indent(indent_level)}if ({line[3:].strip()}) {{")
            block_stack.append("if")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line == "else":
            indent_level -= 1
            output.append(f"{indent(indent_level)}}} else {{")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.lower().startswith("for "):
            parts = line[4:].split('=')
            var = parts[0].strip()
            start, end = map(str.strip, parts[1].replace("to", ",").split(','))
            output.append(f"{indent(indent_level)}for (int {var} = {start}; {var} < {end}; {var}++) {{")
            block_stack.append("for")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.startswith("while "):
            output.append(f"{indent(indent_level)}while ({line[6:].strip()}) {{")
            block_stack.append("while")
            indent_level += 1
            prev_indent = current_indent + 1
        else:
            output.append(f"{indent(indent_level)}// Unsupported: {line}")
            prev_indent = current_indent

    while block_stack:
        indent_level -= 1
        block_stack.pop()
        output.append(f"{indent(indent_level)}}}")

    output.append(f"{indent(1)}return 0;")
    output.append("}")
    return '\n'.join(output)


def transpile_to_python(source_code):
    lines = source_code.strip('\n').splitlines()
    output = []
    indent_level = 0
    block_stack = []
    prev_indent = 0

    for raw_line in lines:
        line = raw_line.strip()
        current_indent = get_indent(raw_line)

        while block_stack and current_indent < prev_indent:
            indent_level -= 1
            block_stack.pop()
            prev_indent -= 1

        if line.startswith("let "):
            var, val = map(str.strip, line[4:].split('=', 1))
            output.append(f"{indent(indent_level)}{var} = {val}")
        elif line.startswith("print "):
            output.append(f"{indent(indent_level)}print({line[6:].strip()})")
        elif line.startswith("if "):
            output.append(f"{indent(indent_level)}if {line[3:].strip()}:")
            block_stack.append("if")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line == "else":
            indent_level -= 1
            output.append(f"{indent(indent_level)}else:")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.lower().startswith("for "):
            parts = line[4:].split('=')
            var = parts[0].strip()
            start, end = map(str.strip, parts[1].replace("to", ",").split(','))
            output.append(f"{indent(indent_level)}for {var} in range({start}, {end}):")
            block_stack.append("for")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.startswith("while "):
            output.append(f"{indent(indent_level)}while {line[6:].strip()}:")
            block_stack.append("while")
            indent_level += 1
            prev_indent = current_indent + 1
        else:
            output.append(f"{indent(indent_level)}# Unsupported: {line}")
            prev_indent = current_indent

    return '\n'.join(output)


def transpile_to_c(source_code):
    lines = source_code.strip('\n').splitlines()
    output = ['#include <stdio.h>', '', 'int main() {']
    indent_level = 1
    block_stack = []
    prev_indent = 0

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        current_indent = get_indent(raw_line)
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        if line != "else":
            while block_stack and current_indent < prev_indent:
                indent_level -= 1
                block_stack.pop()
                output.append(f"{indent(indent_level)}}}")
                prev_indent -= 1

        if line.startswith("let "):
            var, val = map(str.strip, line[4:].split('=', 1))
            output.append(f"{indent(indent_level)}int {var} = {val};")
        elif line.startswith("print "):
            output.append(f"{indent(indent_level)}printf(\"%d\\n\", {line[6:].strip()});")
        elif line.startswith("if "):
            output.append(f"{indent(indent_level)}if ({line[3:].strip()}) {{")
            block_stack.append("if")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line == "else":
            indent_level -= 1
            output.append(f"{indent(indent_level)}}} else {{")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.lower().startswith("for "):
            parts = line[4:].split('=')
            var = parts[0].strip()
            start, end = map(str.strip, parts[1].replace("to", ",").split(','))
            output.append(f"{indent(indent_level)}for (int {var} = {start}; {var} < {end}; {var}++) {{")
            block_stack.append("for")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.startswith("while "):
            output.append(f"{indent(indent_level)}while ({line[6:].strip()}) {{")
            block_stack.append("while")
            indent_level += 1
            prev_indent = current_indent + 1
        else:
            output.append(f"{indent(indent_level)}// Unsupported: {line}")
            prev_indent = current_indent

    while block_stack:
        indent_level -= 1
        block_stack.pop()
        output.append(f"{indent(indent_level)}}}")

    output.append(f"{indent(1)}return 0;")
    output.append("}")
    return '\n'.join(output)


def transpile_to_java(source_code):
    lines = source_code.strip('\n').splitlines()
    output = ['public class Main {', '    public static void main(String[] args) {']
    indent_level = 2
    block_stack = []
    prev_indent = 0

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        current_indent = get_indent(raw_line)
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        if line != "else":
            while block_stack and current_indent < prev_indent:
                indent_level -= 1
                block_stack.pop()
                output.append(f"{indent(indent_level)}}}")
                prev_indent -= 1

        if line.startswith("let "):
            var, val = map(str.strip, line[4:].split('=', 1))
            output.append(f"{indent(indent_level)}int {var} = {val};")
        elif line.startswith("print "):
            output.append(f"{indent(indent_level)}System.out.println({line[6:].strip()});")
        elif line.startswith("if "):
            output.append(f"{indent(indent_level)}if ({line[3:].strip()}) {{")
            block_stack.append("if")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line == "else":
            indent_level -= 1
            output.append(f"{indent(indent_level)}}} else {{")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.lower().startswith("for "):
            parts = line[4:].split('=')
            var = parts[0].strip()
            start, end = map(str.strip, parts[1].replace("to", ",").split(','))
            output.append(f"{indent(indent_level)}for (int {var} = {start}; {var} < {end}; {var}++) {{")
            block_stack.append("for")
            indent_level += 1
            prev_indent = current_indent + 1
        elif line.startswith("while "):
            output.append(f"{indent(indent_level)}while ({line[6:].strip()}) {{")
            block_stack.append("while")
            indent_level += 1
            prev_indent = current_indent + 1
        else:
            output.append(f"{indent(indent_level)}// Unsupported: {line}")
            prev_indent = current_indent

    while block_stack:
        indent_level -= 1
        block_stack.pop()
        output.append(f"{indent(indent_level)}}}")

    output.append('    }')
    output.append('}')
    return '\n'.join(output)
