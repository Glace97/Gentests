import matplotlib.pyplot as plt
import numpy as np

'''
Plot code coverage and branch coverage for different test types.

'''
# Input data full testsuite

data = {
    'Randoop': {'Code coverage': 39, 'Branch coverage': 25},
    'V1 GPT3.5-turbo-16k': {'Code coverage': 52, 'Branch coverage': 43},
    'Human-written': {'Code coverage': 95, 'Branch coverage': 92}
}


'''
data = {
    'V1 GPT3.5-turbo-16k': {'Code coverage': 54, 'Branch coverage': 43},
    'V2 GPT3.5-turbo-16k': {'Code coverage': 55.4, 'Branch coverage': 50.2},
    'V2 GPT4': {'Code coverage': 74.1, 'Branch coverage': 67}
}
'''


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
ax.set_xlabel('Test Generator Methods')
ax.set_ylabel('Coverage (%)')
ax.set_title('Code and Branch Coverage by Different Methods')
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

# Adjusting the y-axis limit
ax.set_ylim(0, max(code_coverage + branch_coverage) * 1.1)  # Setting the upper limit to 110% of the maximum value


# Making layout more compact
plt.tight_layout()

# Showing the plot
plt.show()