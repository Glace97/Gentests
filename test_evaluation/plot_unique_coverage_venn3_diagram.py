import matplotlib.pyplot as plt
from matplotlib_venn import venn3

# Data
unique_randoop = 39
total_randoop = 5419
unique_v1 = 56
total_v1 = 7410
unique_human = 5088
total_human = 13900
overlap_all = 3878
total_executable_lines = 15843

# Total overlaps between each pair (these need to be adjusted for triple overlaps)
overlap_randoop_v1 = (total_randoop + total_v1 - unique_human - total_executable_lines + overlap_all) / 2
overlap_randoop_human = (total_randoop + total_human - unique_v1 - total_executable_lines + overlap_all) / 2
overlap_v1_human = (total_v1 + total_human - unique_randoop - total_executable_lines + overlap_all) / 2

# Calculate the unique parts for the Venn diagram
only_randoop = total_randoop - overlap_randoop_v1 - overlap_randoop_human - overlap_all
only_v1 = total_v1 - overlap_randoop_v1 - overlap_v1_human - overlap_all
only_human = total_human - overlap_randoop_human - overlap_v1_human - overlap_all

# Calculate percentages
percent_only_randoop = (only_randoop / total_executable_lines) * 100
percent_only_v1 = (only_v1 / total_executable_lines) * 100
percent_only_human = (only_human / total_executable_lines) * 100
percent_overlap_randoop_v1 = (overlap_randoop_v1 / total_executable_lines) * 100
percent_overlap_randoop_human = (overlap_randoop_human / total_executable_lines) * 100
percent_overlap_v1_human = (overlap_v1_human / total_executable_lines) * 100
percent_overlap_all = (overlap_all / total_executable_lines) * 100

# Create the Venn diagram
plt.figure(figsize=(10, 10))
venn_diagram = venn3(subsets=(only_randoop, only_v1, overlap_randoop_v1,
                               only_human, overlap_randoop_human, overlap_v1_human, overlap_all),
                     set_labels=('Randoop', 'v1 GPT3.5-turbo-16k', 'Human-written'))

# Update the labels to show percentages
venn_diagram.get_label_by_id('100').set_text(f'{percent_only_randoop:.2f}%')
venn_diagram.get_label_by_id('010').set_text(f'{percent_only_v1:.2f}%')
venn_diagram.get_label_by_id('001').set_text(f'{percent_only_human:.2f}%')
venn_diagram.get_label_by_id('110').set_text(f'{percent_overlap_randoop_v1:.2f}%')
venn_diagram.get_label_by_id('101').set_text(f'{percent_overlap_randoop_human:.2f}%')
venn_diagram.get_label_by_id('011').set_text(f'{percent_overlap_v1_human:.2f}%')
venn_diagram.get_label_by_id('111').set_text(f'{percent_overlap_all:.2f}%')

# Optional: add title and annotations
plt.title('Unique Coverage Comparison Among Test Suites')
plt.annotate(f'Total number of executable lines: {total_executable_lines}', xy=(0.5, -0.1), xycoords='axes fraction',
             ha='center', fontsize=12)

# Show the diagram
plt.show()
