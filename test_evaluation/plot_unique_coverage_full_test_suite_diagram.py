import matplotlib.pyplot as plt
from matplotlib_venn import venn3

# Given data
total_lines = 15843
unique_randoop = 39
total_randoop = 5419
unique_gpt = 56
total_gpt = 7410
unique_human = 5088
total_human = 13900
overlap_all = 3878

# Calculate non-overlapping parts by subtracting overlapping lines from total lines for each suite
randoop_only = total_randoop - overlap_all
gpt_only = total_gpt - overlap_all
human_only = total_human - overlap_all

# Create sets for each test suite
# We simulate the line numbers by assigning consecutive integers
randoop_lines = set(range(1, total_randoop + 1))
gpt_lines = set(range(total_randoop + 1, total_randoop + total_gpt + 1))
human_lines = set(range(total_randoop + total_gpt + 1, total_randoop + total_gpt + total_human + 1))

# Simulating overlap
randoop_lines.update(range(overlap_all))
gpt_lines.update(range(overlap_all))
human_lines.update(range(overlap_all))

# Define the sets for the Venn diagram
sets = [
    randoop_lines,
    gpt_lines,
    human_lines
]

# Calculate intersections and unique areas
venn_labels = {
    '100': len(randoop_lines - gpt_lines - human_lines),
    '010': len(gpt_lines - randoop_lines - human_lines),
    '001': len(human_lines - randoop_lines - gpt_lines),
    '110': len(randoop_lines & gpt_lines) - overlap_all,
    '101': len(randoop_lines & human_lines) - overlap_all,
    '011': len(gpt_lines & human_lines) - overlap_all,
    '111': overlap_all
}

# Plotting the Venn diagram
plt.figure(figsize=(10, 8))
venn_diagram = venn3(subsets=venn_labels, set_labels=('Randoop', 'V1 GPT3.5-turbo-16k', 'Human-Written'))
plt.title("Overlapping Covered Lines of Exectuable Code")
plt.show()
