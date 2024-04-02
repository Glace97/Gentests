import subprocess
import os
import re

'''
Input: Java File (class)
Output: List of all the public methods of that class
'''
def get_all_public_methods(java_file_path):
    # 1. Find classpath
    
    #java_file_path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java"
    directory, java_filename = os.path.split(java_file_path)
    #print(directory)
    #print(java_filename)
    root = directory.split("src/main/java")[0]
    #print("Root: ", root) 
    package = directory.split("src/main/java")[1]
    #print("Package: ", package)
    classname = os.path.splitext(java_filename)[0]

    # DEBUG: Expected:/Users/glacierali/repos/MEX/commons-lang/target/classes/org/apache/commons/lang3/arch/Processor.class
    # Constructing the class path

    class_path = root + "target/classes" + package + "/" + f"{classname}.class"
    #print("Full path: ", class_path)

    # 2. Get all public methods.
    result = subprocess.run(['javap', '-public', class_path], capture_output=True, text=True)

    if result.returncode != 0:
        print("Error running javap command:")
        print(result.stderr)
        return None
    
    public_methods = []
    lines = result.stdout.splitlines()
    for line in lines:
        # Public method lines usually start with "public" keyword
        if line.strip().startswith("public"):
            # Extract method name using regex
            method_name_match = re.match(r'^\s*public\s+\w+\s+(\w+)\(.*', line)
            if method_name_match:
                method_name = method_name_match.group(1)
                public_methods.append(method_name)

    return public_methods
    
'''
Calls the javaparser program, which extracts the given methods and the method body from the java file.
Input: List of methods (names), path to java file
Output: Void
'''
def parse_method_bodies(java_file_path, methods):
  # CLI command: 
  # java -classpath /Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar parser.MethodExtractor <args>
  
  cmd = ["java", 
         "-cp", 
         "/Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
         "parser.MethodExtractor", java_file_path]

  cmd.extend(methods)

  invoke_java_program(cmd)


'''
Calls the javaparser program, which extracts class variables, fields, enums, inner classes, etc.
Input: Path to javafile
Output: Void
'''
def parse_context(java_file_path):
   # CLI command
   # java -classpath /Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar parser.ContextExtractor <args>

  cmd = ["java", 
      "-cp", 
      "/Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
      "parser.ContextExtractor", java_file_path]

  invoke_java_program(cmd)


'''
Creates the prompt for generating unittests.
Format:

You are a coding assistant. 
Generate a junit5 test suite for the following method <Method Name> in the class <Class Name>. The test suite should achieve high coverage and cover all edge cases. 
Input: Name of method to test, path to the parsed methods from the source code, path to the generated context
'''
def construct_prompt(method_name, path_parsed_methods, path_context):

  # 1. Get the parsed method body  
  with open(path_parsed_methods, 'r') as file:
    parsed_methods = file.readlines()

    method_matches = []
    for index, line in enumerate(parsed_methods):
       if method_name in line:
          # Found a method, add content 
          print("We found the methods")
          start = index
          while start > 0:
             if parsed_methods[start].strip() == '':
                break
             start -= 1 

          end = index
          while end < len(parsed_methods):
            if parsed_methods[end].strip() == '':
              break
            end += 1 

          method_body = parsed_methods[start:end]

          print("Found method body: ", method_body)
          method_matches.append(method_body)
    

    # Handle if there are several methods with the same name
    if(len(method_matches) > 1):
       print("TODO: handle this case when we have several methods with the same name")
    elif (len(method_matches) == 1):
       # Get methods body, we have exactly one
       full_method = method_matches[0]
       full_method = ''.join(full_method)


    else:
       print(f"WARNING: No parsed method body found for {method_name}. Will not generate a prompt.")
       return
    
  # 2. Add method to context
  with open(path_context, 'r') as file:
    context = file.read()

  prompt = context + '\n\n' + full_method

  # 3. Save the prompt to a defined output
  with open('./output', 'w') as output:
    output.write(prompt)

################################################  HELPER METHODS ################################################## 

def invoke_java_program(cmd):
    # Invoke context extractor program
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()

  program = cmd[3]

  if process.returncode == 0:
    print(f"Sucessfully invoked program {program}.")
  else:
    print(f"Error occurred while invoking program {program}: ", stderr.decode())



def main():
    # TESTING: Test file
    java_file_path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java"

    # Use case: only javafile provided (test all public methods)
    all_methods = get_all_public_methods(java_file_path)
    
    # Create the prompt
    if(len(all_methods) > 0):
      # Generate a context for the given file:
      parse_context(java_file_path)
      # Get method bodies
      parse_method_bodies(java_file_path, all_methods)
    
    else:
       print('No testable methods found in: java_file_path')

    # TESTING: Test one method
    test_method = all_methods[0]
    path_context = '/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output/Processor_context'
    path_methods = '/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output/Processor_methods'
    construct_prompt(test_method, path_methods, path_context)
    


if __name__ == "__main__":
    
    #If provided only file --> get_all_methods()

    main()