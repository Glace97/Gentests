# Proof of Concept: Gentests 
   
This program is a Proof of Concept (PoC), designed to generate unit tests for a given Java file. It utilizes the OpenAI ChatGPT language model to generate test suites based on provided prompts.  
   
## Usage  
   
To use this program, follow the steps below:  
   
1. Install the required dependencies by running `pip install -r requirements.txt`.  

2. This program requires the compiled Java parser programs (MethodParser, ContextParser and TestFileParser) that are called internally.
Stand in the directory of each project and run `mvn clean package` 
   
3. Run the program by executing the `gentests_template.py` file with the following command:  
   ```  
   python gentests_template.py [javafile] [options]  
   ```  
  
   - `[javafile]`: Path to the Java file for which you want to generate unit tests.  
  
   Available options:  
   - `-m`, `--methods`: Specify a sequence of method names (separated by whitespace) for which you want to generate tests. If not provided, tests will be generated for all methods in the file.  
   - `-o`, `--path_output`: Specify the path where the generated test files will be saved.  
   - `--model`: Choose the language model to use for generating tests. Options are `gpt-3.5-turbo` (default) or `gpt4`.  
   
## Program Structure  
   
The program consists of the following main functions:  
   
- `initialize_llm(model_choice)`: Initializes an instance of the AzureChatOpenAI class based on the specified model choice.  
- `parse_method_bodies(java_file_path, selected_methods)`: Calls the MethodParser program to extract specified methods and their bodies from a Java file.  
- `parse_context(java_file_path)`: Calls the context parser program to extract class variables, fields, enums, inner classes, etc.  
- `construct_prompt(class_name, path_parsed_methods, path_context_folder)`: Creates a prompt for generating unit tests.  
- `prompt_model(location_prompts, class_name, llm)`: Sends a template with function signature to the OpenAI ChatGPT model and writes the generated test suites to temporary files.  
- `construct_testfile(class_name, test_directory)`: Creates a test class by combining the generated test suites for a given class.  
   

## Example Usage
 
Here are some example usages of the program:
- Specify model gpt-3.5-turbo explicitly and selected methods. Test files are placed in the tmp/ folder:
```
python gentests_template.py /path/to/javafile.java -m method1 method2 --model gpt-3.5-turbo -o tmp/  
 ```

- Specify model gpt4 explicitly:
```
python gentests_template.py /path/to/javafile.java -m method1 method2 --model gpt4 -o tmp/  
```

- No model specified, defaults to gpt-3.5-turbo. Generates tests for all methods in the file. Test files are placed in the tmp/ folder:
```
python gentests_template.py /path/to/javafile.java -o tmp/  
```

- Specify model gpt4 explicitly. No methods specified, generates tests for all methods in the file. Test files are placed in the tmp/ folder:
```
python gentests_template.py /path/to/javafile.java --model gpt4 -o tmp/  
```

## Notes

- The generated test files will follow a specific structure and include boilerplate code for JUnit

- v1 folder contains the first implementation of the Proof Of Concept.


