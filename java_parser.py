import re

fun_pattern = r'public\s+(\w+)\s+(\w+)\s*\((.*?)\)'
static_fun_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'


# TODO: 
# 1. fix edgecase if a function occurs within class variable
# 2. remove private functions from metadata



def parse_metadata(): 
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


#'''How to keep track of function scope'''
# if pattern contains { open_brackets = 1
# else read (next) line and open_brackets = 1
# while openbrackest > 0
# for each line
#   if contains {, open_brackets += 1
# print to output file
# print closing bracket


