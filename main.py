#main.py

#We want to take the input Python file and turn it into a .java file
import os
from util import insert_class, translate_line, brace_and_indent, identify_duplicate_variables

def get_lines(file_name):
    lines = []
    if os.path.exists(file_name):
        f = open(file_name, "r")
        for line in f.readlines():
            lines.append(line)
        f.close()
        return lines
    else:
        return "Either your file does not exist or your file does not have a .py extension"

def save_lines(lines):
    name = input("Please enter a name for the file: ")
    name += ".java"
    f = open(name, "w")
    f.write("//This is a new Java File\n")
    f = open(name, "a")
    for line in lines:
        f.write(line + "\n")
    f.close()

def main():
    file_name = input("Please enter a file name: ")
    lines = get_lines(file_name)
    lines = insert_class(lines, file_name)
    variables = identify_duplicate_variables(lines)
    for line in lines:
        line_index = lines.index(line)
        new_line = translate_line(line, variables)
        lines[line_index] = new_line
    new_lines = brace_and_indent(lines)
    new_lines.insert((len(new_lines)-1), "}")
    new_lines.insert((len(new_lines)-1), "}")
    save_lines(new_lines)

main()