import matplotlib.pyplot as plt
import numpy as np

'''
Plot code coverage and branch coverage for different test types.

'''
# Input data
data = {
    'Randoop': {'Code coverage': 39, 'Branch coverage': 25},
    'V1 gpt3.5-turbo-16k': {'Code coverage': 52, 'Branch coverage': 43},
    'Manual': {'Code coverage': 95, 'Branch coverage': 92}
}

# Extracting labels and values
labels = list(data.keys())
code_coverage = [data[label]['Code coverage'] for label in labels]
branch_coverage = [data[label]['Branch coverage'] for label in labels]

# Setting up the positions for the bars
x = np.arange(len(labels))  # the label locations
bar_width = 0.35  # the width of the bars

# Creating the figure and the axes
fig, ax = plt.subplots()

# Creating bars
rects1 = ax.bar(x - bar_width/2, code_coverage, bar_width, label='Code Coverage')
rects2 = ax.bar(x + bar_width/2, branch_coverage, bar_width, label='Branch Coverage')

# Adding some text for labels, title and custom x-axis tick labels, etc.
ax.set_xlabel('Test Types')
ax.set_ylabel('Coverage (%)')
ax.set_title('Code and Branch Coverage by Test Types')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Function to attach a text label above each bar in *rects*, displaying its height.
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

# Calling the function to annotate the bars
autolabel(rects1)
autolabel(rects2)

# Making layout more compact
plt.tight_layout()

# Showing the plot
plt.show()