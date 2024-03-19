import re
import subprocess

# TODO: add other types of functions we want to match against
# Pattern matches any type of function with a docstring prior
function_pattern = r'(?:/\*\*[^{;]*?\*/\s*)?.*(public|private).*?\([\s\S]*?\)\s*{'

# Might not need?
def read_function_block(java_code, start_pos):
    brace_count = 0
    pos = start_pos
    while pos < len(java_code):
        if java_code[pos] == '{':
            brace_count += 1
        elif java_code[pos] == '}':
            brace_count -= 1
            if brace_count == 0:
                return pos
        pos += 1
    return -1  # If the end of the function is not found

def parse_metadata(src_path, class_path):     
    last_class_var = get_last_class_variable(class_path)
    lines, metadata_break_point = find_variable_end_line(src_path, last_class_var)
    metadata = lines[:metadata_break_point]
    #print(metadata)

    # Extract content up to the matched position
    file_name = f'metadata_{get_class_name(src_path)}.txt'
    with open(file_name, 'w') as output_file:
        for line in metadata:
            output_file.write(line)

# ------------------------------------------------ HELPER/DEBUG METHODS -----------------------------------------------------------
            
# Find all testable public methods and subsequent javadoc comments prior to method.
def find_public_methods(path):
    # Pattern matches public functions with or without docstrings
    pattern = r'(/\*\*[\s\S]*?\*/\s*)?.*?public.*\([\s\S]*?\)\s*{' 
    with open(path, 'r') as file:
        contents = file.read()
    public_functions = find_matches(pattern, contents)
            
    # DEBUG
    # _print_matches(public_functions)
    return public_functions

# DEBUG    
def _print_matches(matches):
    for match_text, start_index, end_index in matches:
        print(f"Match: {match_text}, Start Index: {start_index}, End Index: {end_index}")

# Useful for creating corresponding files
def get_class_name(path):
    # Get the class name given a .java file
    split_dir = path.split('/')
    file = split_dir[len(split_dir) - 1] # file = <class_name>.<file extension>
    class_name = file.split('.')[0]
    return class_name

# General method to find any match
def find_matches(content, pattern):
    matches = re.finditer(pattern, content)
    result = []
    for match in matches:
        match_text = match.group()
        start_index = match.start()
        end_index = match.end()
        result.append((match_text, start_index, end_index))
    return result

# Return the given line, of the last variable
def find_variable_end_line(java_file, variable_name):
    with open(java_file, 'r') as file:
        lines = file.readlines()
        content = ''.join(lines)
        pattern = r'(?<=\b' + re.escape(variable_name) + r'\b).*?(?=[;,])'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            end_line = content.count('\n', 0, match.end()) + 1
            return lines, end_line
        else:
            return None

# Using javap, find the last class variable
def get_last_class_variable(class_path):
    # Run javap command
    try:
        output = subprocess.check_output(['javap', '-private', class_path], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")
        return None

    # Find the last class variable
    class_variable_pattern = r"(\w+)\s+(\w+);"
    class_variables = re.findall(class_variable_pattern, output)

    if class_variables:
        last_class_variable = class_variables[-1][1]
        return last_class_variable
    else:
        print("No class variables found.")
        return None

def main():
    with open('java_class_pairs_test.txt', 'r') as input:
        lines = input.readlines()

    for line in lines:
        pair = line.split(' ')
        java_file_path = pair[0]
        class_path = pair[1]
        parse_metadata(java_file_path, class_path)

    #remove_private_funcs('metadata.txt')

if __name__ == "__main__":
    main()