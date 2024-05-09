import matplotlib.pyplot as plt
from matplotlib_venn import venn3

# Given data
total_lines = 4518
unique_v1 = 190
total_v1 = 1906
unique_v2 = 174
total_v2 = 2827
unique_gpt4 = 388
total_gpt4 = 3164
overlap_all = 1363

# Calculating the only parts for each set by adjusting the total number for only overlaps
v1_only = total_v1 - overlap_all
v2_only = total_v2 - overlap_all
gpt4_only = total_gpt4 - overlap_all

# Create sets for each test suite
# We simulate the line numbers by assigning consecutive integers
v1_lines = set(range(1, total_v1 + 1))
v2_lines = set(range(total_v1 + 1, total_v1 + total_v2 + 1))
gpt4_lines = set(range(total_v1 + total_v2 + 1, total_v1 + total_v2 + total_gpt4 + 1))

# Simulating the overlapping area to adjust for the correct size
v1_lines.update(range(overlap_all))
v2_lines.update(range(overlap_all))
gpt4_lines.update(range(overlap_all))

# Define the sets for the Venn diagram
sets = [
    v1_lines,
    v2_lines,
    gpt4_lines
]

# Calculate intersections and unique areas
venn_labels = {
    '100': len(v1_lines - v2_lines - gpt4_lines),
    '010': len(v2_lines - v1_lines - gpt4_lines),
    '001': len(gpt4_lines - v1_lines - v2_lines),
    '110': len(v1_lines & v2_lines) - overlap_all,
    '101': len(v1_lines & gpt4_lines) - overlap_all,
    '011': len(v2_lines & gpt4_lines) - overlap_all,
    '111': overlap_all
}

# Plotting the Venn diagram
plt.figure(figsize=(10, 8))
venn_diagram = venn3(subsets=venn_labels, set_labels=('V1 GPT3.5-turbo-16k', 'V2 GPT3.5-turbo-16k', 'V2 GPT4'))
plt.title("Overlapping Covered Lines of Executable Code")
plt.show()
