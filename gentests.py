import subprocess
import os
import re

import argparse
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
import dotenv


# Initialize model
dotenv.load_dotenv()
llm = AzureChatOpenAI(deployment_name="gpt-35-turbo-16k-SSNA",model_name="gpt-35-turbo-16k")

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

  invoke_java_parsers(cmd)

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

  invoke_java_parsers(cmd)

'''
Creates the prompt for generating unittests.
Format:

You are a coding assistant. 
Generate a junit5 test suite for the following method <Method Name> in the class <Class Name>. The test suite should achieve high coverage and cover all edge cases. 
Input: Name of method to test, path to the parsed methods from the source code (maybe one or several), path to the generated context
Returns: location of constructed prompts
'''
def construct_prompt(methods, class_name, path_parsed_methods, path_context_folder):

  # 1. Create output folder for all prompts (1 prompt/method of the same name)
  location_prompts = f'./prompts/{class_name}'
  os.makedirs(location_prompts, exist_ok=True)

  for method_name in methods: 
    # 2. Get the parsed method body  
    with open(os.path.join(path_parsed_methods, method_name), 'r') as file:
      parsed_methods = file.read()
    
    # Imports and context are separate to facilitate further parsing
    path_imports = path_context_folder + "/imports"
    path_context = path_context_folder + "/context"
    
    # 3. Construct final prompt
    with open(path_imports, 'r') as file:
      imports = file.read()

    with open(path_context, 'r') as file:
      context = file.read()
    
    # TODO: Beautify? + add javadoc comment prior to class decleration
    code = imports + f'\nclass {class_name}' + ' {\n' + context + '\n'+ parsed_methods + '}'
    query = f'You are a coding assistant. Generate a junit5 test suite for the method {method_name}. The test suite should achieve high coverage and cover all edge cases. \n\n'
    
    # TODO: Check wether I can add more details AFTER the code to make the output more desireable.
    final_prompt = query + code
    
    with open(os.path.join(location_prompts, method_name), 'w') as output:
      output.write(final_prompt)
    
  # Where to find the created prompts
  return location_prompts

'''
Sends the prompt to the openAI chatGPT model.
Input: Location to prompts, where each prompt is one textfile containing a query, context and function(s) to be tested. All prompts belong to the same class.
'''
def prompt_model(location_prompts, class_name):
  # 1. Location of responses
  location_ai_response = f'./model_responses/{class_name}'
  os.makedirs(location_ai_response, exist_ok=True)

  for prompt_file in os.listdir(location_prompts):
     # 2. For each promptfile, send it to the model
     path_to_prompt = os.path.join(location_prompts, prompt_file)
     
     #print("file name: " + prompt_file)

     with open(path_to_prompt, 'r') as file:
        prompt = file.read()
        ai_response = llm.invoke(prompt)
        
        # 3. Trim the response
        full_content = ai_response.content
        print("Full content \n")
        print(full_content)
        print('\n\n')

        # Model may respond with explanations aside from code, extract codeblock
        pattern = r"```java.*?```"
        match = re.search(pattern, full_content, re.DOTALL)

        if(match):
          print("match found")
          # Remove code block backticks
          generated_tests = match.group(0).replace('```java', '').rerplace('```', '') 
        else:
          print("no match found")
          # We might have recieved only code with no backticks.
          generated_tests = full_content

        # 4. Save the reponse for creation of testfile
        with open(os.path.join(location_ai_response, prompt_file), 'w') as output:
          output.write(generated_tests)



################################################  HELPER METHODS ################################################## 

def invoke_java_parsers(cmd):
  # Invoke context extractor program
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()

  # Format: java -cp <classpath> <program> <args....>
  program = cmd[3]

  if process.returncode == 0:
    print(f"Sucessfully invoked program {program}.")
  else:
    print(f"Error occurred while invoking program {program}: ", stderr.decode())

def main():
    # TESTING: Test file
    #java_file_path = "/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java"

    
    # TODO: run gentests as application and not with python
    # Example: python gentests.py  /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java -m is32bit is64bit
    gentests = argparse.ArgumentParser(description="Generate unit tests for a given javafile.")
    gentests.add_argument("javafile", type=str, help="Path to the Java file")
    gentests.add_argument("-m", "--methods", nargs="*", help="Sequence of methodnames separated by whitespace")

    args = gentests.parse_args()

    java_file_path = args.javafile

    if args.methods:
      # Use case 1: javafile and specific methods provided.
      # -m methodName1 methodName2
      all_methods = args.methods
    else:
      # Use case 2: only javafile provided (test all public methods)
      all_methods = get_all_public_methods(java_file_path) # List of all methods.
      
    # Create the prompt
    if(len(all_methods) > 0):
      # Generate a context for the given file:
      parse_context(java_file_path)
      # Get method bodies
      parse_method_bodies(java_file_path, all_methods)

      # TODO: change to tmp/ folder once fixed in parser
      _, java_filename = os.path.split(java_file_path)
      class_name = os.path.splitext(java_filename)[0]
      path_context = f'/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output/{class_name}_context'
      path_methods = f'/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output/{class_name}_methods'
      location_prompts = construct_prompt(all_methods, class_name, path_methods, path_context)

      prompt_model(location_prompts, class_name)

    else:
       print('No testable methods found in: java_file_path')


    
if __name__ == "__main__":
    main()