'''
This version also accounts for the human written tests.
'''
import xml.etree.ElementTree as ET
import csv
import os


def extract_covered_lines(jacoco_report):
    tree = ET.parse(jacoco_report)
    root = tree.getroot()

    covered_lines = set()
    executable_lines = 0
    for package in root.findall(".//package"):
        for sourcefile in package.findall(".//sourcefile"):
            # Check if the current sourcefile is in the list of classes we care about
            for line in sourcefile.findall(".//line"):
                executable_lines += 1
                if int(line.get("ci")) > 1:
                    # ci == 0, no hit. Number corresponding to number of hits.
                    covered_lines.add((sourcefile.get("name"), int(line.get("nr"))))
    return covered_lines, executable_lines

def compare_reports(report1, report2, report3):
    covered_lines1, _ = extract_covered_lines(report1)
    covered_lines2, executable_lines = extract_covered_lines(report2)
    covered_lines3, _ = extract_covered_lines(report3)

    unique_lines1 = covered_lines1 - covered_lines2 - covered_lines3
    unique_lines2 = covered_lines2 - covered_lines1 - covered_lines3
    unique_lines3 = covered_lines3 - covered_lines1 - covered_lines2

    overlapping_lines = covered_lines1 & covered_lines2 & covered_lines3
    return unique_lines1, unique_lines2, unique_lines3, covered_lines1, covered_lines2, covered_lines3, overlapping_lines, executable_lines


##############################################################################################################################################################


# Paths to the three JaCoCo reports
# Paths to the two JaCoCo reports
randoop_coverage_report = "/Users/glacierali/repos/MEX/reports/jacoco_randoop/jacoco.xml"
poc_coverage_report = "/Users/glacierali/repos/MEX/reports/jacoco_1st_poc/jacoco.xml"
manual = "/Users/glacierali/repos/MEX/reports/jacoco_manual/jacoco.xml"

# Compare the three reports considering only the specified classes
unique_lines_randoop, unique_lines_v1_gpt35, unique_lines_manual, all_lines_randoop, all_lines_v1_gpt35, all_lines_manual, overlapping_lines, executable_lines = compare_reports(
    randoop_coverage_report, poc_coverage_report, manual)

print("Unique covered lines lines by randoop:")
for line in unique_lines_randoop:
    print(line)

print("\nUnique covered lines by v1 gpt3.5-turbo-16k:")
for line in unique_lines_v1_gpt35:
    print(line)

print("\nUnique covered lines by manually written tests:")
for line in unique_lines_manual:
    print(line)

print(f'Number of unique lines covered by randoop: {len(unique_lines_randoop)}')
print(f'Total number of lines covered by randoop: {len(all_lines_randoop)}')

print(f'Number of unique lines covered by v1 gpt3.5-turbo: {len(unique_lines_v1_gpt35)}')
print(f'Total number of lines covered by v1 gpt3.5-turbo: {len(all_lines_v1_gpt35)}')

print(f'Number of unique lines covered by human written tests: {len(unique_lines_manual)}')
print(f'Total number of lines covered by v2 human written tests: {len(all_lines_manual)}')

print(f'Overlapping number of lines by all test suites {len(overlapping_lines)}')
print(f'Total number of executable lines: {executable_lines}')


