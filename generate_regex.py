import subprocess
import os

def run_javap(class_path):
    # Construct the command to run javap
    command = ['javap', '-p', class_path]
    
    try:
        # Run the javap command
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        path = class_path.split('/')
        class_name = path[len(path) - 1]
        with open(f'disassembled/raw/{class_name}.txt', "w") as output_file:
            output_file.write(result.stdout)
    
    except subprocess.CalledProcessError as e:
        # If the command returns a non-zero exit code, print the error message
        print("Error:", e.stderr)


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.class'):
                class_path = os.path.join(root, file)
                run_javap(class_path)


# Example usage:
dir = '/Users/glacierali/repos/MEX/commons-lang/target/classes/org/apache/commons/lang3/'
process_directory(dir)