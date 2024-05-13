'''
This version also accounts for the human written tests.
'''
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles

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

    # Create Venn diagram
    plt.figure(figsize=(8, 6))

    # For 2 sets
    #venn2(subsets=(len(covered_lines1 - overlapping_lines), len(covered_lines2 - overlapping_lines), len(overlapping_lines)), set_labels=('Randoop', 'V1 GPT3.5-turbo-16k'))

    # Extract the counts of elements for each part of the Venn diagram
    venn_counts = [len(covered_lines1 - covered_lines2 - covered_lines3), len(covered_lines2 - covered_lines1 - covered_lines3), len(covered_lines1 & covered_lines2 - covered_lines3),
                len(covered_lines3 - covered_lines1 - covered_lines2), len(covered_lines1 & covered_lines3 - covered_lines2), len(covered_lines2 & covered_lines3 - covered_lines1),
                len(covered_lines1 & covered_lines2 & covered_lines3)]
    
    venn_labels = ('Randoop', 'V1 GPT3.5-turbo-16k', 'Human-written')
    venn = venn3(subsets=venn_counts, set_labels=venn_labels)

    plt.title("Unique Coverage and Overlap of executable lines of Code")
    plt.show()

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


