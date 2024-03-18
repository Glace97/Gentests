
import subprocess
import re
'''
Approach: find the last class var and create breakpoint at that point.
Problem: it only stops at the variable name, we do not know when it "ends"
'''
def generate_regex_pattern(class_file):
    # Run javap command
    try:
        output = subprocess.check_output(['javap', '-private', class_file], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")
        return None

    # Find the last class variable
    class_variable_pattern = r"(\w+)\s+(\w+);"
    class_variables = re.findall(class_variable_pattern, output)

    if class_variables:
        last_class_variable = class_variables[-1][1]
        # Generate regex pattern for the last class variable
        regex_pattern = fr'\b{last_class_variable}\b'
        return regex_pattern
    else:
        print("No class variables found.")
        return None

def get_last_class_variable(class_file):
    # Run javap command
    try:
        output = subprocess.check_output(['javap', '-private', class_file], stderr=subprocess.STDOUT, universal_newlines=True)
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

# Example usage
if __name__ == "__main__":
    class_file = "/Users/glacierali/repos/MEX/commons-lang/target/classes/org/apache/commons/lang3/ArrayUtils.class"
    regex_pattern = generate_regex_pattern(class_file)
    if regex_pattern:
        print("Regex pattern for the last class variable:", regex_pattern)

    variablename = get_last_class_variable(class_file)
    print("variable name: ", variablename)