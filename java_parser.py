import re

fun_pattern = r'public\s+(\w+)\s+(\w+)\s*\((.*?)\)'
static_fun_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'


# TODO: 
# 1. fix edgecase if a function occurs within class variable
# 2. remove private functions from metadata

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


def remove_private_funcs(file):
    # Read metadata
    with open(file, "r") as input_file:
        meta_data = input_file.read()
    
    # Patterns
    # TODO: add patterns wherre there is no docstring prior
    docstring_protected_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*protected\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    docstring_protected_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*protected\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    docstring_private_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    docstring_private_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    
    patterns = [docstring_protected_pattern, docstring_protected_static_pattern, docstring_private_pattern, docstring_private_static_pattern]
    
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




def parse_metadata(): 
    #TODO: add pattern to the variable names
    doc_string_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'
    doc_string_static_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*(?:public\s+static\s+)?(?:\w+\s+)?\w+\s+\w+\s*\((?:.*?)\)'

    path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/AnnotationUtils.java"

    with open(path, "r") as input_file:
        java_code = input_file.read()

    # Find the first match for either pattern in the Java code
    match1 = re.search(doc_string_fun, java_code, re.DOTALL)
    match2 = re.search(doc_string_static_fun, java_code, re.DOTALL)

    if match1 and match2:
        # Determine which match occurred first
        if match1.start() < match2.start():
            match = match1
        else:
            match = match2
    elif match1:
        match = match1
    elif match2:
        match = match2
    else:
        match = None

    if match:
        # Extract content up to the matched position
        content_before_match = java_code[:match.start()]
        
        # Write the extracted content to the output file
        with open('metadata.txt', 'w') as output_file:
            output_file.write(content_before_match)


def main():
    remove_private_funcs('metadata.txt')

if __name__ == "__main__":
    main()