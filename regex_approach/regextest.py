import re

def find_matching_text(file_path, pattern):
    with open(file_path, 'r') as file:
        contents = file.read()
        matches = re.finditer(pattern, contents)
        result = []
        for match in matches:
            match_text = match.group()
            start_index = match.start()
            end_index = match.end()
            result.append((match_text, start_index, end_index))
        return result

# Example usage
file_path = 'LuhnCalculator.java'
pattern = r'(/\*\*[\s\S]*?\*/\s*)?.*?public.*\([\s\S]*?\)\s*{'  

matches = find_matching_text(file_path, pattern)
for match_text, start_index, end_index in matches:
    print(f"Match: {match_text}, Start Index: {start_index}, End Index: {end_index}")
