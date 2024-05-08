import matplotlib.pyplot as plt
from matplotlib_venn import venn2

# Data
unique_randoop = 1519
total_randoop = 5419
unique_poc = 3510
total_poc = 7410
overlap = 3900
total_executable_lines = 15843

# Calculate the unique parts for the Venn diagram
only_randoop = total_randoop - overlap  # total Randoop coverage minus overlapping coverage
only_poc = total_poc - overlap          # total POC coverage minus overlapping coverage

# Calculate percentages
percent_only_randoop = (only_randoop / total_executable_lines) * 100
percent_only_poc = (only_poc / total_executable_lines) * 100
percent_overlap = (overlap / total_executable_lines) * 100

# Create the Venn diagram
plt.figure(figsize=(8, 8))
venn_diagram = venn2(subsets=(only_randoop, only_poc, overlap),
                     set_labels=('Randoop', 'V1 gpt3.5-turbo-16k'))

# Update the labels to show percentages
venn_diagram.get_label_by_id('10').set_text(f'{percent_only_randoop:.2f}%')
venn_diagram.get_label_by_id('01').set_text(f'{percent_only_poc:.2f}%')
venn_diagram.get_label_by_id('11').set_text(f'{percent_overlap:.2f}%')

# Optional: add title and annotations
plt.title('Uniqe Coverage Comparison between Randoop and V1 gpt3.5-turbo-16k')
plt.annotate(f'Total number of executable lines: {total_executable_lines}', xy=(0.5, -0.1), xycoords='axes fraction',
             ha='center', fontsize=10)

# Show the diagram
plt.show()
