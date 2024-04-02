import re
import subprocess


def parse_metadata(src_path, class_path):     
    print("Start parsing;", get_class_name(src_path))
    with open(src_path, 'r') as file:
        lines_of_code = file.readlines()
    
    full_content = ''.join(lines_of_code)

    # Pattern matches any type of function with a docstring prior
    function_pattern = r'(?:/\*\*[^{]*?\*/\s*)?.*(public|private|protected|native).*?\([\s\S]*?\)\s*{'
    metadata_break_point = find_line_of_pattern(full_content, function_pattern)
    if(metadata_break_point):
        #print("Found first function on index: ", metadata_break_point)
        metadata_break_point = include_javadoc_comment(metadata_break_point, lines_of_code)
        #print("Breakpoint index: ", metadata_break_point)
        metadata = ''.join(lines_of_code[:metadata_break_point])
        #print(metadata)
    else: 
        metadata = full_content

    # Extract content up to the matched position
    file_name = f'metadata/metadata_{get_class_name(src_path)}.txt'
    with open(file_name, 'w') as output_file:
        for line in metadata:
            output_file.write(line)
        print("Done with ", get_class_name(src_path))

# ------------------------------------------------ HELPER/DEBUG METHODS -----------------------------------------------------------
# Keep track of {} scope
def read_block(java_code, start_pos):
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

# Return the end of line of the given pattern, if found
def find_line_of_pattern(full_content, pattern):
    match = re.search(pattern, full_content)
    #print("Found match: ", match)
    if match:
        end_line_index = full_content.count('\n', 0, match.end())
        return end_line_index
    else:
        return None


# If there is a javadoc comment, return the line above
def include_javadoc_comment(line, lines_of_code):
    prev = line - 1
    prefixes = ('/**', '*', '*/')
    start_of_line = lines_of_code[prev].split()[0]
    while (start_of_line.startswith(prefixes) or '@' in start_of_line) and prev > 0:
        prev -= 1
        if lines_of_code[prev].split():
            start_of_line = lines_of_code[prev].split()[0] 
        else:
            # newline reached
            break
    return prev

def main():
    with open('java_class_pairs.txt', 'r') as input:
        lines = input.readlines()

    for line in lines:
        pair = line.split(' ')
        java_file_path = pair[0].strip()
        class_path = pair[1].strip()
        #print("Java file path: ", java_file_path)
        #print("Class path: ", class_path)
        parse_metadata(java_file_path, class_path)

if __name__ == "__main__":
    main()