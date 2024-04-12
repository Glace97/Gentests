import xml.etree.ElementTree as ET

def remove_failing_tests(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for testcase in root.findall('.//testcase'):
        failure = testcase.find('failure')
        error = testcase.find('error')

        if failure is not None or error is not None:
            # If either failure or error element exists, remove the testcase
            root.remove(testcase)

    # Write the modified XML tree to a new file
    new_xml_file = xml_file.replace('.xml', '_filtered.xml')
    tree.write(new_xml_file)

    print(f"Failing tests removed. Filtered test results saved to: {new_xml_file}")

if __name__ == "__main__":
    xml_file_path = "/Users/glacierali/repos/MEX/poc/test_evaluation/reports/Test Results - java_in_commons-lang3.xml"
    remove_failing_tests(xml_file_path)
