import subprocess
import os
import re
import shutil
import argparse
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
import dotenv

# Initialize model
dotenv.load_dotenv()
llm = AzureChatOpenAI(deployment_name="gpt-35-turbo-16k-SSNA",model_name="gpt-35-turbo-16k")


#TODO add support for c#
#TODO invoke javaparser for parsing output. One file/class
#TODO change path so that it maps to the homefolder (currently hardcoded to my local absolute path)

'''
Calls the javaparser program, which extracts the given methods and the method body from the java file.
Input: List of methods (names), path to java file
Output: Void
'''
def parse_method_bodies(java_file_path, selected_methods):
  # CLI command: 
  # java -classpath /Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar parser.MethodExtractor <args>
  
  cmd = ["java", 
         "-cp", 
         "/Users/glacierali/repos/MEX/poc/Parser/target/classes:/Users/glacierali/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
         "parser.MethodExtractor", java_file_path]

  # May or may not contain arguments
  # If selected methods is empty, we test all methods by default
  if(len(selected_methods) > 0):
    cmd.extend(selected_methods)

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
Format: Generate a junit5 test suite for the following method {method_name}. The test suite should achieve high coverage and cover all edge cases. 
Input: Name of method to test, path to the parsed methods from the source code (maybe one or several), path to the generated context
Returns: location of constructed prompts
'''
def construct_prompt(class_name, path_parsed_methods, path_context_folder,):

  # 1. Create output folder for all prompts (1 prompt/method of the same name)
  location_prompts = f'./prompts/{class_name}'
  os.makedirs(location_prompts, exist_ok=True)

  for method_filename in os.listdir(path_parsed_methods): 
    # 2. Get the parsed method body  
    method_name = os.path.splitext(method_filename)[0]
    
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
    query = f'Generate a junit5 test suite for the method {method_name}. The test suite should achieve high coverage and cover all edge cases. \n\n'
    
    # TODO: Check wether I can add more details AFTER the code to make the output more desireable.
    final_prompt = query + code
    
    with open(os.path.join(location_prompts, method_name), 'w') as output:
      output.write(final_prompt)
    
  # Where to find the created prompts
  return location_prompts

'''
Sends the prompt to the openAI chatGPT model.
Input: Location to prompts, where each prompt is one textfile containing a query, context and function(s) to be tested. All prompts belong to the same class.
Output: Writes each testsuite for a given function to a file, under ./model_responses/{class_name}/{methodName}
'''
def prompt_model(location_prompts, class_name):
  # 1. Location of responses
  location_ai_response = f'./model_responses/{class_name}'
  os.makedirs(location_ai_response, exist_ok=True)
  
  # The name of the promptfile corresponds to the name of the method
  for prompt_file in os.listdir(location_prompts):
     # 2. For each promptfile, send it to the model
     path_to_prompt = os.path.join(location_prompts, prompt_file)
     
     #print("file name: " + prompt_file)

     with open(path_to_prompt, 'r') as file:
        prompt = file.read()
        print("Making the first invokation for ", file)
        ai_response = llm.invoke(prompt)
        
        # 3. Extract code content from response
        full_content = ai_response.content
        #print("Full content \n")
        #print(full_content)
        #print('\n\n')

        # Model may respond with explanations aside from code, extract codeblock
        pattern = r"```java.*?```"
        match = re.search(pattern, full_content, re.DOTALL)

        if(match):
          #print("match found")
          # Remove code block backticks
          generated_test_class = match.group(0).replace('```java', '').replace('```', '') 
        else:
          #print("no match found")
          # We might have recieved only code with no backticks.
          generated_test_class = full_content

        #4. Model typically responds with entire testclass, extract the @Test methods
        print("Making the second invokation for ", file)
        second_prompt = f'{generated_test_class}\n\nFilter out only the @Test test functions. Java code: // Your Java code here'
        ai_response = llm.invoke(second_prompt)
        generated_tests = ai_response.content
        
        print("Performing some formatting to generated tests for file: ", file)
        # Write the generated tests, with indentation
        indentation = "    "  # Four spaces for indentation
        lines = generated_tests.split('\n')
        indented_code = [indentation + line for line in lines]
        generated_tests_indented = '\n'.join(indented_code)
        print("Writing final output; the generated tests for file: ", file)
        with open(os.path.join(location_ai_response, prompt_file), 'w') as output:
          output.write(generated_tests_indented)
  print("Done prompting the model.")

'''
Creats a test class by combining the generated testsuites (1 file /method) for a given class.
Applies basic heuristics.
Input: path to generated tests, name of CUT, location of where the testclass should be placed.
Output: A full testclass with the test suite inserted in the given test directory.
'''            
def construct_testfile(class_name, test_directory):
  #1. Create output directory
  with open(f'./parser_output/{class_name}_context/package', 'r') as input:
    original_pkg = input.read()

  if len(original_pkg) > 0:
    pkg = original_pkg.split(' ')[1]
    pkg = pkg.split(';')[0]
    package_path = pkg.replace('.', '/')
    # Typical java test directory: src/test/java
    output_dir = os.path.join(test_directory, package_path)
    os.makedirs(output_dir, exist_ok=True)
  else:
    output_dir = test_directory
    os.makedirs(test_directory, exist_ok=True)
  
  #2. Add package and basic imports.
  with open('./junit_imports', 'r') as input:
    imports = input.read()
    imports = imports + '\n\n'
  output_file = os.path.join(output_dir, f'{class_name}Test.java')
  class_declaration = f'public class {class_name}Test ' + '{\n'
  
  with open(output_file, 'w') as output:
    if len(original_pkg) > 0:
      output.write(original_pkg) 
    output.write(imports)
    output.write(class_declaration)
    
    tests = os.listdir(f'./model_responses/{class_name}')
    # Add the generated the unit tests
    for method_specific_tests in tests:
      path_method_specific_test = os.path.join(f'./model_responses/{class_name}', method_specific_tests)
      with open(path_method_specific_test, 'r') as input:
        tests = input.read()
        output.write(tests)
        output.write('\n')
    
    # Closing bracket
    output.write('\n}')

  


'''
Remove generated methods and context folders for the given class under test.
Also removes the generated prompts.
'''
def cleanup(class_name):
   path_context = f'/Users/glacierali/repos/MEX/poc/parser_output/{class_name}_context'
   path_methods = f'/Users/glacierali/repos/MEX/poc/parser_output/{class_name}_methods'
   prompts = f'/Users/glacierali/repos/MEX/poc/prompts/{class_name}'
   try:
     shutil.rmtree(path_methods)
     shutil.rmtree(path_context)
     shutil.rmtree(prompts)
     print(f"Folders: \n '{path_context}, \n{path_methods} \n {prompts}' successfully removed.")
   except OSError as e:
     print(f"Error: : {e.strerror}")


################################################  HELPER METHODS ################################################## 

def invoke_java_parsers(cmd):
  # Invoke context extractor program
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()

  # Format: java -cp <classpath> <program> <args....>
  program = cmd[3]

  #print("\n\nrunning command: ", cmd)
  #print("\n\n")

  if process.returncode == 0:
    print(f"Sucessfully invoked program {program}.")
  else:
    print(f"Error occurred while invoking program {program}: ", stderr.decode())



'''
Example use case 1:
    python gentests.py  /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java -m is32bit is64bit
Path to file is provided, -m flag to denote that specific methods are chosen.

Example use case 2:
    python gentests.py  /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java
Only path to file provided as arg. Will generate tests for all public methods.
'''
def main():
    
    # TODO: run gentests as application and not with python
    # Examples: 
    # python gentests.py  /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java -m is32bit is64bit -o ~/tmp
    # python gentests.py /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/ArchUtils.java -o /Users/glacierali/repos/MEX/commons-lang/src/test/java
    gentests = argparse.ArgumentParser(description="Generate unit tests for a given javafile.")
    gentests.add_argument("javafile", type=str, help="Path to the Java file")
    gentests.add_argument("-m", "--methods", nargs="*", help="Sequence of methodnames separated by whitespace")
    gentests.add_argument("-o", "--path_output", type=str, help="Generated testfiles ara placed in the given path.")

    args = gentests.parse_args()
    java_file_path = args.javafile

    if args.methods:
      # Use case 1: javafile and specific methods provided.
      # -m methodName1 methodName2
      selected_methods = args.methods
    else:
      selected_methods = []  
    
    # Must define output path
    if args.path_output is None:
      print("Please provide a path for the output.")
      return
    
    output_path = args.path_output

    print("Generating tests for: ", java_file_path)
    # Create the prompt
    # Generate a context for the given file:
    #parse_context(java_file_path)
    
    # Get method bodies
    #parse_method_bodies(java_file_path, selected_methods)

    # TODO: change to tmp/ folder once fixed in parser
    _, java_filename = os.path.split(java_file_path)
    class_name = os.path.splitext(java_filename)[0]
    path_context = f'/Users/glacierali/repos/MEX/poc/parser_output/{class_name}_context'
    path_methods = f'/Users/glacierali/repos/MEX/poc/parser_output/{class_name}_methods'
    location_prompts = construct_prompt(class_name, path_methods, path_context)
    prompt_model(location_prompts, class_name)

    construct_testfile(class_name, output_path)

    #cleanup(class_name)
    print("Done generating tests for: ", java_file_path)
    
if __name__ == "__main__":
    main()