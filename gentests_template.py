import subprocess
import os
import re
import shutil
import argparse
from langchain_openai import AzureChatOpenAI
import dotenv
import concurrent.futures


def initialize_llm(model_choice):
  """
  initialize_llm(model_choice)
  --------------------------

  Initializes an instance of the AzureChatOpenAI class based on the specified model choice.

  :param model_choice: The choice of the model. 'gpt4' for GPT-4, else defaults to GPT-3.5-Turbo.
  :type model_choice: str

  :return: An instance of AzureChatOpenAI initialized with the chosen model.
  :rtype: AzureChatOpenAI
  """

  # Default setting is gpt-3.5-turbo  
  dotenv.load_dotenv()
  if model_choice == 'gpt4':
    # Overriding the default deployment name for gpt4
    print("INFO: Using GPT-4 model.")
    deployment_name = 'gpt-4-SSNA-playground'  # Update this to your GPT-4 deployment name
    llm = AzureChatOpenAI(deployment_name=deployment_name, model_name="gpt-4")
  else:
    print("INFO: Using GPT3.5-Turbo model.")
    deployment_name = os.getenv('OPENAI_DEPLOYMENT_NAME')
    llm = AzureChatOpenAI(deployment_name=deployment_name, model_name="gpt-35-turbo-16k")
  
  return llm

def parse_method_bodies(java_file_path, selected_methods):
  '''
  parse_method_bodies(java_file_path, selected_methods)
  -----------------------------------------------------

  Calls the MethodParser program to extract specified methods and their bodies from a Java file.

  :param java_file_path: Path to the Java file to parse.
  :type java_file_path: str
  :param selected_methods: List of method names to extract. If empty, all methods are parsed.
  :type selected_methods: list[str]

  :return: None
  :rtype: None
  '''
  method_parser_path = os.path.join(os.path.dirname(__file__), "MethodParser")
  print("path to method_parser programme: ", method_parser_path)
  cmd = ["java", 
         "-cp", 
         f"{method_parser_path}/target/classes:{os.path.expanduser('~')}/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
         "parser.MethodExtractor", java_file_path]

  # print("making invokation for method parser")
  # May or may not contain arguments
  # If selected methods is empty, we test all methods by default
  if(len(selected_methods) > 0):
    # print("Selected methods: ", selected_methods)
    cmd.extend(selected_methods)

  invoke_java_parsers(cmd)

def parse_context(java_file_path):
  '''
  parse_context(java_file_path)
  -----------------------------

  Calls the context parser program to extract class variables, fields, enums, inner classes, etc.

  :param java_file_path: Path to the Java file to parse.
  :type java_file_path: str

  :return: None
  :rtype: None
  '''
  context_parser_path = os.path.join(os.path.dirname(__file__), "ContextParser")
  #print("path to context_parser programme: ", context_parser_path)
  cmd = ["java", 
         "-cp", 
         f"{context_parser_path}/target/classes:{os.path.expanduser('~')}/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
         "parser.ContextExtractor", java_file_path]

  invoke_java_parsers(cmd)

def construct_prompt(class_name, path_parsed_methods, path_context_folder,):
  '''
  construct_prompt(class_name, path_parsed_methods, path_context_folder)
  ----------------------------------------------------------------------

  Creates a prompt for generating unit tests.

  :param class_name: Name of the class containing the method to test.
  :type class_name: str
  :param path_parsed_methods: Path to the parsed methods from the source code.
  :type path_parsed_methods: str
  :param path_context_folder: Path to the generated context.
  :type path_context_folder: str

  :return: Location of constructed prompts.
  :rtype: str
  '''
  # 1. Create output folder for all prompts (1 prompt/method of the same name)
  location_prompts = f'./prompts/{class_name}'
  os.makedirs(location_prompts, exist_ok=True)

  for method_filename in os.listdir(path_parsed_methods): 
    # 2. Get the parsed method body  
    method_name = os.path.splitext(method_filename)[0]
    
    with open(os.path.join(path_parsed_methods, method_name), 'r') as file:
      parsed_methods = file.read()
    
    # Imports and context are separate to facilitate further parsing
    path_package = path_context_folder + "/package"
    path_imports = path_context_folder + "/imports"
    path_context = path_context_folder + "/context"
    path_class_declaration = path_context_folder + "/declaration"

    # 3. Construct final prompt
    with open(path_package, 'r') as file:
      project_package = file.read()

    with open(path_imports, 'r') as file:
      imports = file.read()

    with open(path_context, 'r') as file:
      context = file.read()

    with open(path_class_declaration, 'r') as file:
      class_declaration = file.read()

    # TODO: Beautify? + add javadoc comment prior to class decleration
    code = f'{project_package}\n{imports}\nclass {class_declaration}' + ' {\n' + context + '\n'+ parsed_methods + '}'
    
    # Template for the prompt
    final_prompt = f"""
Generate unit tests for {method_name}() in class {class_name} using JUnit5 and Mockito. The tests should strictly follow the provided boilerplate structure. Here’s the boilerplate for each test method:

{project_package}    
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import org.junit.jupiter.api.Test;
//Additional imports here

public class {class_name}Test {{

    @Test
    public void ExampleTest() {{
        // Instantiate all necessary variables here

        // Write the test code here following the given rules
    }}
}}

// Code to be tested
{code}

Rules to Follow:
1. All variables should be instantiated within the test method itself.
2. Do not access any private variables, methods, or classes directly.
3. Use Mockito for mocking dependencies and JUnit for assertions.
4. The test suite should aim to achieve high code and branch coverage, also identifying and testing edge cases.
5. Deliver the test suite in a single, cohesive code block.
6. ONLY deliver the test suite. Do not include any additional code or comments.
"""
    
    with open(os.path.join(location_prompts, method_name), 'w') as output:
      output.write(final_prompt)
    
  # Where to find the created prompts
  return location_prompts

def prompt_model(location_prompts, class_name, llm):
  '''
  prompt_model(location_prompts, class_name, llm)
  ----------------------------------------------

  Sends prompts to the OpenAI ChatGPT model and writes the generated test suites to files.

  :param location_prompts: Location of the prompt files, each containing a query, context, and function(s) to be tested.
  :type location_prompts: str
  :param class_name: Name of the class to which all prompts belong.
  :type class_name: str
  :param llm: The language model instance to use for generating responses.
  :type llm: AzureChatOpenAI

  :return: None
  :rtype: None
  '''

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

    # Use ThreadPoolExecutor to handle the API invocation
     with concurrent.futures.ThreadPoolExecutor() as executor:
      future = executor.submit(invoke_llm, llm, prompt)
      try:         
        print("Invoke model for ", prompt_file)

        # Wait for the invoke function to return or timeout after 300 seconds (5 minutes)
        ai_response = future.result(timeout=300)
        
        print("Invokation done.")

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

        print("Writing final output; the generated tests for file: ", file)
        outputfile = prompt_file + ".java"
        with open(os.path.join(location_ai_response, outputfile), 'w') as output:
          #output.write(generated_tests_indented)
          output.write(generated_test_class)
      except concurrent.futures.TimeoutError:
        print("Invocation timed out after 5 minutes.")
        raise TimeoutError("The API call timed out after 5 minutes.")
      except Exception as e: 
        print("Error occurred while invoking model: ", e)
        print("Prompt (file): ", prompt_file)
        if 'ai_response' in locals():
          print("Model response: ", ai_response)
          
  print("Done prompting the model.")

def construct_testfile(class_name, test_directory):
  '''
  construct_testfile(class_name, test_directory)
  ----------------------------------------------

  Creates a test class by combining the generated test suites (one file per method) for a given class.

  :param class_name: Name of the class under test (CUT).
  :type class_name: str
  :param test_directory: Location where the test class should be placed.
  :type test_directory: str

  :return: None
  :rtype: None
  '''

  #1. Create output directory if it does not exist
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
  

  output_file = os.path.join(output_dir, f'{class_name}Test.java')
  generated_tests_path = os.path.join(os.path.dirname(__file__), f'model_responses/{class_name}')
  tests = os.listdir(generated_tests_path)
  

  for i, method_named_test_suite_file in enumerate(tests):
    print("Will add tests for method: ", method_named_test_suite_file)
    method_specific_test_suite_path = os.path.join(generated_tests_path, method_named_test_suite_file)
    print("checking if testfile exists: ", output_file)
    if os.path.exists(output_file):
        print("Output file exists")
        # File exists, parse the content of the new testclass and merge it in to the existing test suite
        testfile_parser_path = os.path.join(os.path.dirname(__file__), "TestFileParser")
        cmd = ["java", 
         "-cp", 
         f"{testfile_parser_path}/target/classes:{os.path.expanduser('~')}/.m2/repository/org/antlr/antlr4-runtime/4.13.1/antlr4-runtime-4.13.1.jar", 
         "parser.TestFileParser", output_file, method_specific_test_suite_path]
        
        print("Sending the following arguments: ", output_file, method_specific_test_suite_path)
        invoke_java_parsers(cmd)

        # The test class now including tests generated for the givene method
        reconstructed_test_class_path = f'./parser_output/{class_name}Test_reconstructed/{class_name}Test.java'
        print("reconstructed_test_class", reconstructed_test_class_path)
        shutil.copy(reconstructed_test_class_path, output_file)
        # 1. Save the merged testclass
        local_save_for_debug = f'./reconstructed_testclasses/{class_name}'
        os.makedirs(local_save_for_debug, exist_ok=True)
        save_for_debug = os.path.join(local_save_for_debug, f'iteration_{i}.java')
        shutil.copy(reconstructed_test_class_path, save_for_debug)
    else:
        # File does not exist, create a new test class
        print("Create testfile from scratch")
        shutil.copy(method_specific_test_suite_path, output_file)
        print("Created new testfile for method: ", method_named_test_suite_file)




################################################  HELPER METHODS ################################################## 


def cleanup(class_name):
   '''
    cleanup(class_name)
    -------------------

    Removes generated files after the test generation process is completed.

    :param class_name: Name of the class for which files were generated.
    :type class_name: str

    :return: None
    :rtype: None
    '''
   path_context = f'./parser_output/{class_name}_context'
   path_methods = f'./parser_output/{class_name}_methods'
   prompts = f'./prompts/{class_name}/'
   model_responses = f'./model_responses/{class_name}/'
   reconstructed_test_class = f'./parser_output/{class_name}Test_reconstructed/'
   reconstructed_test_class_iter = f'./reconstructed_testclasses/{class_name}/'
   try:
    shutil.rmtree(path_methods)
    print(f"Folder '{path_methods}' successfully removed.")
    shutil.rmtree(path_context)
    print(f"Folder '{path_context}' successfully removed.")
    shutil.rmtree(prompts)
    print(f"Folder '{prompts}' successfully removed.")
    shutil.rmtree(model_responses)
    print(f"Folder '{model_responses}' successfully removed.")
    shutil.rmtree(reconstructed_test_class)
    print(f"Folder '{reconstructed_test_class}' successfully removed.")
    shutil.rmtree(reconstructed_test_class_iter)
    print(f"Folder '{reconstructed_test_class_iter}' successfully removed.")
   except OSError as e:
     print(f"Error: : {e.strerror}")



def invoke_java_parsers(cmd):
  '''
  invoke_java_parsers(cmd)
  -------------------------

  Invokes the Java parser programs.

  :param cmd: Command to invoke the Java parser program.
  :type cmd: list[str]

  :return: None
  :rtype: None
  '''

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

def invoke_llm(llm, prompt):
  '''
  invoke_llm(llm, prompt)
  ------------------------

  Invokes the provided language model instance to generate a response based on the given prompt.

  :param llm: The language model instance to use for generating the response.
  :type llm: AzureChatOpenAI
  :param prompt: The prompt to generate a response for.
  :type prompt: str

  :return: The response generated by the language model.
  :rtype: str
  '''
  return llm.invoke(prompt)


def main(): 
    '''
    main()
    ----

    Main method of the program to generate unit tests for a given Java file.

    Usage Examples:
        # Specify model gpt-3.5-turbo explicitly and selected methods. Testfile placed in tmp/ folder
        python gentests_template.py /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java -m is32Bit is64Bit --model gpt-3.5-turbo -o tmp/
        
        # Specify model gpt4 explicitly
        python gentests_template.py /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java -m is32Bit is64Bit --model gpt4 -o tmp/

        # No model specified, defaults to gpt-3.5-turbo. Generates tests for all methods in the file. Testfile placed in tmp/ folder
        python gentests_template.py /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java -o tmp/
        
        # Specify model gpt4 explicitly. No methods specified, generates tests for all methods in the file. Testfile placed in tmp/ folder
        python gentests_template.py /Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3/arch/Processor.java --model gpt4 -o tmp/

    :return: None
    :rtype: None
    '''
    gentests = argparse.ArgumentParser(description="Generate unit tests for a given javafile.")
    gentests.add_argument("javafile", type=str, help="Path to the Java file")
    gentests.add_argument("-m", "--methods", nargs="*", help="Sequence of methodnames separated by whitespace")
    gentests.add_argument("-o", "--path_output", type=str, help="Generated testfiles ara placed in the given path.")
    gentests.add_argument("--model", choices=['gpt-3.5-turbo', 'gpt4'], default='gpt-3.5-turbo', 
                          help="Choose the language model to use for generating tests (default: gpt-3.5-turbo)")

    args = gentests.parse_args()
    java_file_path = args.javafile
    selected_methods = args.methods or [] 
    chosen_model = args.model or ''

    # Must define output path
    if args.path_output is None:
      print("Please provide a path for the output.")
      return
    
    output_path = args.path_output

    # Initilize the language model
    llm = initialize_llm(chosen_model)

    print("Generating tests for: ", java_file_path)
    
    # Create the prompt
    # Generate a context for the given file:
    parse_context(java_file_path)
    
    # Get method bodies
    parse_method_bodies(java_file_path, selected_methods)

    # TODO: change to tmp/ folder once fixed in parser
    _, java_filename = os.path.split(java_file_path)
    class_name = os.path.splitext(java_filename)[0]
    current_directory = os.getcwd()
    path_context = os.path.join(current_directory, 'parser_output', f'{class_name}_context')
    #print("path context: ", path_context)
    path_methods = os.path.join(current_directory, 'parser_output', f'{class_name}_methods')
    #print("path methods: ", path_methods)
    location_prompts = construct_prompt(class_name, path_methods, path_context)
    prompt_model(location_prompts, class_name, llm)

    construct_testfile(class_name, output_path)

    cleanup(class_name)
    print("Done generating tests for: ", java_file_path)
    
if __name__ == "__main__":
    main()