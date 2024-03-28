import subprocess
import os
import re


def get_all_public_methods(java_file_path):
    # 1. Find classpath
    
    java_file_path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java"
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
    

def parse_javadoc_comment(file):
  
  # CLI command: 
  # java -classpath /Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar parser.MethodExtractor
  
  cmd = ["java", 
         "-cp", 
         "/Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
         "parser.MethodExtractor"]
  
  # Add arguments to command, methods to test¨
  # javap command on given file.
  # We can find the path to classfile in java_class_pairs.txt file
  # Extract name of all public methods methods which we are interested in


  # Invoke method extractor program
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()  

  

def main():
    methods = get_all_public_methods("test")
    
    print(methods)

if __name__ == "__main__":
    
    #If provided only file --> get_all_methods()

    main()