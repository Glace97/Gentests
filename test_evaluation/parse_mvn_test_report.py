import re
import csv

def parse_maven_report(report):
    data = []
    pattern_with_errors = r'\[INFO\] Running (.+)\n\[ERROR\] Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: (\d+\.\d+) s <<< FAILURE! -- in (.+)'
    pattern_without_errors = r'\[INFO\] Running (.+)\n\[INFO\] Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: (\d+\.\d+) s -- in (.+)'

    matches_with_errors = re.findall(pattern_with_errors, report)
    matches_without_errors = re.findall(pattern_without_errors, report)

    for match in matches_with_errors:
        #print(match)
        class_name, num_tests, num_failures, num_errors, num_skipped, _, _ = match
        data.append((class_name, int(num_tests), int(num_failures), int(num_errors), int(num_skipped)))

    for match in matches_without_errors:
        class_name, num_tests, _, _, num_skipped, _, _ = match
        data.append((class_name, int(num_tests), 0, 0, int(num_skipped)))
    
    return data

def write_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Class Name', 'Number of Tests', 'Number of Failures', 'Number of Errors', 'Number of Skipped'])
        for row in data:
            writer.writerow(row)

def main():
    with open('./reports/mvn_output_cleaned_tests.txt', 'r') as file:
        report = file.read()

    parsed_data = parse_maven_report(report)
    write_to_csv(parsed_data, 'test_summary.csv')

if __name__ == "__main__":
    main()
