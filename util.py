import re

def insert_class(lines, file_name):
    new_file_name = remove_py_extension(file_name)
    main_line_index = 0
    class_name = "public class " + new_file_name + ":"
    for line in lines:
        if "def main()" in line:
            main_line_index = lines.index(line)
    java_main_line = "public static void main(String[] args):"
    lines[main_line_index] = java_main_line
    class_name_index = max(0, (main_line_index-1))
    lines.insert(class_name_index, class_name)
    #lines.insert((len(lines)-1), "}")
    return lines

def remove_py_extension(file_name):
    dot = file_name.find(".")
    return file_name[:dot]

def initialise_variable(variable, value):
    string_var = re.compile(r'^".{2,}"$')
    char_var = re.compile(r"^'.'$")
    int_var = re.compile(r'^\d+$')
    double_var = re.compile(r'^\d+\.\d+$')
    boolean_var = re.compile(r'^(True|False)$', re.IGNORECASE)
    new_line = ""
    if int_var.match(value):
            new_line = "int " + variable.strip() + "= " + value + ";"
    elif double_var.match(value):
            new_line = "double " + variable.strip() + "= " + value + ";"
    elif boolean_var.match(value):
            new_line = "boolean " + variable.strip() + "= " + value.lower() + ";"
    elif string_var.match(value):
            new_line = "String " + variable.strip() + "= " + value + ";"
    elif char_var.match(value):
            new_line = "char " + variable.strip() + "= " + value + ";"
    else:
        new_line += variable
    return new_line

def translate_variable(line, variables):
    line = str(line)
    string_var = re.compile(r'^".{2,}"$')
    char_var = re.compile(r"^'.'$")
    int_var = re.compile(r'^\d+$')
    double_var = re.compile(r'^\d+\.\d+$')
    boolean_var = re.compile(r'^(True|False)$', re.IGNORECASE)
    assignment = line.find("=")
    variable = line[:assignment]
    value = line[assignment+2:]
    new_line = ""
    if variable in variables and variables[variable]==1:
        new_line = initialise_variable(variable, value)
    else:
        new_line += variable + assignment + value
    return new_line


def translate_line(line, variables):
    line = str(line)
    pattern = re.compile(r'^[^=]*=[^=]*$')
    new_line = line
    current_indent = find_indentation_level(line)
    if ":" not in line:
        if "print(" in line and "f\"" not in line:
            left_bracket = line.find("(")
            right_bracket = line.find(")")
            output = line[left_bracket:right_bracket]
            new_line = "System.out.println" + output + ")"
        elif pattern.match(line):
            new_line = translate_variable(line, variables)
        return str(current_indent*" ")+ new_line + ";"
    else:
        if "if" in line or "while" in line or "else" in line:
            new_line = translate_conditionals(line)
        else:
            new_line = line
    return str(current_indent*" ")+ new_line

def translate_conditionals(line):
    line = str(line)
    and_pattern = re.compile(r'\band\b')
    or_pattern = re.compile(r'\bor\b')
    not_pattern = re.compile(r'\bnot\b')
    if_pattern = re.compile(r'\bif\b')
    while_pattern = re.compile(r'\bwhile\b')
    else_pattern = re.compile(r'\belse\b')

    words = line.split()

    for i, word in enumerate(words):
        if and_pattern.match(word):
            words[i] = word.replace("and", "&&")
        elif or_pattern.match(word):
            words[i] = word.replace("or", "||")
        elif not_pattern.match(word):
            words[i] = word.replace("not", "!")
        elif if_pattern.match(word) or while_pattern.match(word):
            space = word.find(" ")
            words[i] = word[space+1:] + "("
        elif else_pattern.match(word):
            words[i] = word.replace("else", "else{")
        elif ":" in word:
            colon = word.index(":")
            words[i] = word[:colon] + ")" + word[colon:]
    
    return " ".join(words)

def insert_user_input(lines):
    import_util = "import java.util.*;"
    scanner_line = "Scanner sc = new Scanner(System.in);"
    scanner_name = "sc"
    main_index = find_main_line(lines)
    methods = {"boolean": "nextBoolean()", "double": "nextDouble()", "int" : "nextInt()", "String" : "nextLine()"}
    lines.insert(0, import_util)
    lines.insert(main_index+1, scanner_line)
    return lines

def find_main_line(lines):
    for line in lines:
        if "def main()" in line:
            return lines.index(line)
        
def identify_duplicate_variables(lines):
    variables = dict()
    variable = ""
    pattern = re.compile(r'.+?=.+?')
    for line in lines:
        if not pattern.match(line):
            pass
        else:
            assignment = line.find("=")
            variable = line[:assignment]
            if variable in variables:
                variables[variable] += 1
            else:
                variables[variable] = 1
    return variables
            
def find_indentation_level(line):
    return len(line) - len(line.lstrip())

def nest_lines(lines, start=0, min_indent=0):
    nested_lines = []
    i = start
    while i < len(lines):
        current_indent = find_indentation_level(lines[i])
        if current_indent > min_indent:
            # Recursively process the nested block
            nested_block, new_start = nest_lines(lines, i, current_indent)
            #nested_lines.append(" " * current_indent)
            nested_lines.append(nested_block)
            nested_lines.append(" " * current_indent + "}")
            i = new_start
        elif current_indent == min_indent:
            nested_lines.append(lines[i])
            i += 1
        else:
            # End of the current block
            break

    return "\n".join(nested_lines), i

def arrange_lines(lines):
    nested_structure, _ = nest_lines(lines)
    return nested_structure.split("\n")

def brace_and_indent(lines):
    braced_lines = insert_braces(lines)
    new_lines = arrange_lines(braced_lines)
    return new_lines

def find_fc_indices(lines):
    #func_pattern = re.compile(r'^[^\(\)]+\(.*\)$')
    #class_pattern = re.compile(r'\bclass\b')
    indices = []
    for line in lines:
        if ":" in line:
            n = lines.index(line)
            indices.append(n)
    return indices

def insert_braces(lines):
    new_lines = []
    indices = find_fc_indices(lines)
    for i, line in enumerate(lines):
        if i in indices:
            colon = line.find(":")
            new_line = line[:colon] + "{"
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return new_lines


"""
Still to-do:
- user input
- conditionals
- selection, iteration
- strings
- collections
"""