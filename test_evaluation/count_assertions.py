import os
import re
import csv

# Count the total number of assertions
assertion_functions = [
    "assertArrayEquals",
    "assertIterableEquals",
    "assertLinesMatch",
    "assertEquals",
    "assertNotEquals",
    "assertTrue",
    "assertFalse",
    "assertNotNull",
    "assertNotSame",
    "assertNull",
    "assertSame",
    "assertAll",
    "assertThrows",
    "assertThrowsExactly",
    "assertDoesNotThrow",
    "assertTimeout",
    "assertTimeoutPreemptively",
    "assertInstanceOf"
]

# Define the directory to search
directory = "/Users/glacierali/repos/MEX/commons-lang/src/test/java/org/apache/commons/lang3"

# Initialize counters for each assertion function
counts = {func: 0 for func in assertion_functions}

# Define a function to count occurrences of assertion functions in a file
def count_assertions_in_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        for func in assertion_functions:
            if len(re.findall(r"\b" + func + r"\b", content)) > 0:
                # Found match
                counts[func] += len(re.findall(r"\b" + func + r"\b", content)) - 1 # Remove the import which is also matched
                if func == 'assertNotSame':
                    # We have accidently added a duplicate import of this assertion
                    counts[func] -= 1

# Recursively search for Java files in the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".java"):
            count_assertions_in_file(os.path.join(root, file))

# Print the counts
for func, count in counts.items():
    print(f"{func}: {count}")

# Write the results to a CSV file
output_file = "assertion_counts.csv"
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Assertion Function", "Frequency"])
    for func, count in counts.items():
        writer.writerow([func, count])

print(f"Results have been written to {output_file}.")