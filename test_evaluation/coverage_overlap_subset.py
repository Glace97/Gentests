import xml.etree.ElementTree as ET
import csv
import os

def ensure_directory_exists(filepath):
    # Ensure the directory exists
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_covered_lines(jacoco_report, classes_of_interest):
    tree = ET.parse(jacoco_report)
    root = tree.getroot()

    covered_lines = set()
    executable_lines = 0
    for package in root.findall(".//package"):
        for sourcefile in package.findall(".//sourcefile"):
            # Check if the current sourcefile is in the list of classes we care about
            if sourcefile.get("name").split('.')[0] in classes_of_interest:
                for line in sourcefile.findall(".//line"):
                    executable_lines += 1
                    if int(line.get("ci")) > 1:
                        # ci == 0, no hit. Number corresponding to number of hits.
                        covered_lines.add((sourcefile.get("name"), int(line.get("nr"))))
    return covered_lines, executable_lines

def compare_reports(report1, report2, report3, classes_of_interest):
    covered_lines1, _ = extract_covered_lines(report1, classes_of_interest)
    covered_lines2, executable_lines = extract_covered_lines(report2, classes_of_interest)
    covered_lines3, _ = extract_covered_lines(report3, classes_of_interest)

    unique_lines1 = covered_lines1 - covered_lines2 - covered_lines3
    unique_lines2 = covered_lines2 - covered_lines1 - covered_lines3
    unique_lines3 = covered_lines3 - covered_lines1 - covered_lines2

    overlapping_lines = covered_lines1 & covered_lines2 & covered_lines3
    return unique_lines1, unique_lines2, unique_lines3, covered_lines1, covered_lines2, covered_lines3, overlapping_lines, executable_lines


##############################################################################################################################################################

# Define the list of classes of interest
classes_of_interest = ["Processor", "AnnotationUtils", "ArrayUtils", "CharSequenceUtils", 
                       "CharUtils", "ClassUtils", "Functions", "LongRange", "ObjectUtils", "StringUtils"]

# Paths to the three JaCoCo reports
v1_report = "/Users/glacierali/repos/MEX/reports/jacoco_randoop/jacoco.xml"
v2_gpt35_report = "/Users/glacierali/repos/MEX/reports/jacoco_v2_gpt3.5_poc/jacoco.xml"
v2_gpt4_report = "/Users/glacierali/repos/MEX/reports/jacoco_v2_gpt4/jacoco.xml"

# Compare the three reports considering only the specified classes
unique_lines_v1, unique_lines_v2_gpt35, unique_lines_v2_gpt4, all_lines_v1, all_lines_v2_gpt35, all_lines_v2_gpt4, overlapping_lines, executable_lines = compare_reports(
    v1_report, v2_gpt35_report, v2_gpt4_report, classes_of_interest)

print("Unique covered lines lines by v1:")
for line in unique_lines_v1:
    print(line)

print("\nUnique covered lines by v2 gpt3.5-turbo:")
for line in unique_lines_v2_gpt35:
    print(line)

print("\nUnique covered lines by v2 gpt4:")
for line in unique_lines_v2_gpt4:
    print(line)

print(f'Number of unique lines covered by v1: {len(unique_lines_v1)}')
print(f'Total number of lines covered by v1: {len(all_lines_v1)}')

print(f'Number of unique lines covered by v2 gpt3.5-turbo: {len(unique_lines_v2_gpt35)}')
print(f'Total number of lines covered by v2 gpt3.5-turbo: {len(all_lines_v2_gpt35)}')

print(f'Number of unique lines covered by v2 gpt4: {len(unique_lines_v2_gpt4)}')
print(f'Total number of lines covered by v2 gpt4: {len(all_lines_v2_gpt4)}')

print(f'Overlapping number of lines by all models {len(overlapping_lines)}')
print(f'Total number of executable lines: {executable_lines}')


