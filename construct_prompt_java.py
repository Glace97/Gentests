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
    # Test file
    java_file_path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java"
    
    # Generate a context for the given file:
    parse_context(java_file_path)
    
    # Use case: only javafile provided (test all public methods)
    all_methods = get_all_public_methods(java_file_path)
    
    # Get method bodies
    parse_method_bodies(java_file_path, all_methods)

    


if __name__ == "__main__":
    
    #If provided only file --> get_all_methods()

    main()