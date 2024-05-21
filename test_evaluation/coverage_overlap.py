import xml.etree.ElementTree as ET
from matplotlib_venn import venn2
import matplotlib.pyplot as plt

def extract_covered_lines(jacoco_report):
    tree = ET.parse(jacoco_report)
    root = tree.getroot()

    covered_lines = set()
    executable_lines = 0
    for package in root.findall(".//package"):
        for sourcefile in package.findall(".//sourcefile"):
            for line in sourcefile.findall(".//line"):
                executable_lines += 1
                if line.get("ci") > "1":
                    # ci == 0, no hit. Number corresponding to number of hits.
                    covered_lines.add((sourcefile.get("name"), int(line.get("nr"))))
    return covered_lines, executable_lines

def compare_reports(report1, report2):
    covered_lines1, executable_lines = extract_covered_lines(report1)
    covered_lines2, _ = extract_covered_lines(report2)

    unique_lines1 = covered_lines1 - covered_lines2
    unique_lines2 = covered_lines2 - covered_lines1

    return unique_lines1, unique_lines2, covered_lines1, covered_lines2, executable_lines

# Paths to the two JaCoCo reports
randoop_coverage_report = "/Users/glacierali/repos/MEX/reports/jacoco_randoop/jacoco.xml"
poc_coverage_report = "/Users/glacierali/repos/MEX/reports/jacoco_1st_poc/jacoco.xml"

# Compare the two reports
unique_lines1, unique_lines2, covered_lines1, covered_lines2, executable_lines = compare_reports(randoop_coverage_report, poc_coverage_report)

print("Unique covered lines in randoop coverage report:")
for line in unique_lines1:
    print(line)

print("\nUnique covered lines in poc coverage report:")
for line in unique_lines2:
    print(line)

print(f'Number of unique lines covered by randoop: {len(unique_lines1)}')
print(f'Total number of lines covered by randoop: {len(covered_lines1)}')
print(f'Number of unique lines covered by poc (gpt): {len(unique_lines2)}')
print(f'Total number of lines covered by poc (gpt): {len(covered_lines2)}')
print(f'Overlapping number of lines coverd by randoop and poc (gpt) {len(covered_lines1 & covered_lines2)}')
print(f'Total number of executable lines: {executable_lines}')


# Create sets for Venn diagram
set1 = set(len(unique_lines1))
set2 = set(len(unique_lines2))
intersection = len(covered_lines1 & covered_lines2)

# Plot Venn diagram
venn2(subsets=(set1, set2, intersection), set_labels=('Randoop', 'POC (GPT)'))

plt.title("Venn Diagram of Coverage")
plt.show()