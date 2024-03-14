import re

fun_pattern = r'public\s+(\w+)\s+(\w+)\s*\((.*?)\)'
static_fun_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'


# TODO: 
# 1. fix edgecase if a function occurs within class variable
# 2. remove private functions from metadata
# 3. Remove license info

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


#TODO: rename, removes protected funcs as well
def remove_private_funcs(file):
    # Read metadata
    with open(file, "r") as input_file:
        meta_data = input_file.read()
    
    # Patterns
    # TODO: add patterns wherre there is no docstring prior
    docstring_prot_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*protected\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    docstring_prot_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*protected\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    docstring_priv_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    docstring_priv_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    priv_fun_pattern = r'private\s+(\w+)\s+(\w+)\s*\((.*?)\)'
    priv_static_fun_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+\w+\s+\w+\s*\((?:.*?)\)'
    
    patterns = [docstring_prot_pattern,
                docstring_prot_static_pattern, 
                docstring_priv_pattern, 
                docstring_priv_static_pattern, 
                priv_fun_pattern, 
                priv_static_fun_pattern]
    
    # Loop through metadata and remove private functions
    while True:
        # Flag to check if any match was found
        match_found = False

        for pattern in patterns:
            match = re.search(pattern, meta_data, re.DOTALL)
            if match:
                # Match found, read function block
                start_pos = match.start()
                end_pos = read_function_block(meta_data, start_pos)

                if end_pos != -1:
                    # Remove the function block from metadata
                    meta_data = meta_data[:start_pos] + meta_data[end_pos + 1:]
                    match_found = True
                    break 

        # If no match was found, break the loop
        if not match_found:
            break

    # Write the modified metadata back to the file
    with open('trimmed_metadata.txt', "w") as output_file:
        output_file.write(meta_data)


def parse_metadata(path): 
    match_all_pattern = r'(?:/\*\*.*?\*/\s*)?(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'

    with open(path, "r") as input_file:
        java_code = input_file.read()

    # Find the first function (or possible docstring prior to function)
    match = re.search(match_all_pattern, java_code)
    print('match: ', match)

    if match:
        # Extract content up to the matched position
        content_before_match = java_code[:match.start()]
        
        # Write the extracted content to the output file as metadata
        with open('metadata.txt', 'w') as output_file:
            output_file.write(content_before_match)


def main():
    path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/ArrayFill.java"
    parse_metadata(path)
    #remove_private_funcs('metadata.txt')

if __name__ == "__main__":
    main()