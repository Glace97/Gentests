import re

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


def parse_metadata(path): 
    # Pattern matches any type of function
    #function_pattern = r'(/\*\*[\s\S]*?\*/\s*)?.*?(public|private|protected|static|final|abstract)?\s*\b[\w<>]+\s+\w+\s*\(.*?\)\s*{'
    #function_pattern = r'(/\*\*[\s\S]*?\*/\s*)?.*?(public|private|protected|static|final|abstract).*\([\s\S]*?\)\s*{' 
    function_pattern = r'(/\*\*[\s\S]*?\*/\s*)?.*?public.*\([\s\S]*?\)\s*{'
    
    with open(path, "r") as input_file:
        java_code = input_file.read()

    class_declaration_pos = find_class_declaration_pos(java_code)
    if class_declaration_pos:
        # In case of there being javadoc comments prior to class, avoid accidentally pattern matching against it        
        remaining_code = java_code[class_declaration_pos:]
        
        matches = find_matches(remaining_code, function_pattern)
        # Everything before the first method is considered metadata context
        if matches:
            firtst_match, start_pos, end_pos = matches[0]        
            #print("entire match ", firtst_match)
        if start_pos:
            # Extract content up to the matched position
            content_before_match = remaining_code[:start_pos]
            partial_metadata = java_code[:class_declaration_pos-1]

            file_name = f'metadata_{get_class_name(path)}.txt'
            with open(file_name, 'w') as output_file:
                output_file.write(partial_metadata)
                output_file.write(content_before_match)


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
    
def find_class_declaration_pos(content):
    class_declaration_pattern = r"(public\s+)?(\w+\s+)?class\s+(.*?)?\{"  

    class_declaration = re.search(class_declaration_pattern, content)
    if class_declaration:
     return class_declaration.start()

# HELPER/DEBUG METHODS
def _print_matches(matches):
    for match_text, start_index, end_index in matches:
        print(f"Match: {match_text}, Start Index: {start_index}, End Index: {end_index}")

def get_class_name(path):
    # Get the class name given a .java file
    split_dir = path.split('/')
    file = split_dir[len(split_dir) - 1] # file = <class_name>.<file extension>
    class_name = file.split('.')[0]
    return class_name

def find_matches(content, pattern):
    matches = re.finditer(pattern, content)
    result = []
    for match in matches:
        match_text = match.group()
        if 'class' in match_text:
            # Pattern might match to javadoc comments prior to class declarations
            # Do not include 
            continue
        start_index = match.start()
        end_index = match.end()
        result.append((match_text, start_index, end_index))
    return result



def main():
    test_files = [
        "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/ArrayFill.java",
        "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/ArrayUtils.java",
        "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/AnnotationUtils.java",
       "testclasses/LuhnCalculator.java"
    ]
    
    for path in test_files:
        #matches = find_public_methods(path)
        parse_metadata(path)
    
    #remove_private_funcs('metadata.txt')

if __name__ == "__main__":
    main()