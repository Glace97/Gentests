import sys
import os
import subprocess
import argparse

'''
Takes an entire project; and will generate tests for the source code.
'''


'''
Skip abstract classes, annotation classes, interfaces and package-info files.
A very simple and not robust solution.
'''
def check_if_valid_class(file, path):
    with open(path, 'r') as input:
        content = input.read()

    if ('abstract class' in content or 
        'interface' in content or 
        '@interface' in content or 
        file == 'package-info.java'):
        return False
    else:
        return True


def run_gentests_for_java_files(directory, path_output):
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a Java file
            if file.endswith(".java"):
                java_file_path = os.path.join(root, file)
                valid = check_if_valid_class(file, java_file_path)
                if valid:
                    # Call gentests.py with the path to the Java file
                    subprocess.run(["python", "gentests.py", java_file_path, "-o", path_output])


def main():
    parser = argparse.ArgumentParser(description="Check and run tests for Java files.")
    parser.add_argument("directory", type=str, help="Path to the project directory")
    parser.add_argument("-o", "--path_output", type=str, help="Output path")
    args = parser.parse_args()
    
    directory = args.directory

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory.")
        return 1

    if args.path_output is None:
        print("Please provide an output path")

    run_gentests_for_java_files(directory, args.path_output)

if __name__ == "__main__":
    main()