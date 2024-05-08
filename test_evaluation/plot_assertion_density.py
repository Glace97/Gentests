import matplotlib.pyplot as plt
import numpy as np

# Row labels and data
rows = ["Randoop", "V1 gpt3.5-turbo-16k", "Manual"]
data = {
    "Assertion Density per LoC": [6368/30502, 5871/30502, 22201/30502],
    "Assertion Density per Unit Test": [6368/1379, 5871/6235, 22201/4195]
}

# Create figure and axis
fig, ax1 = plt.subplots()

# X axis locations for the groups
index = np.arange(len(rows))
bar_width = 0.35
opacity = 0.8

# Plotting bars for "Assertion Density per LoC" on the primary y-axis
bars1 = ax1.bar(index - bar_width/2, data["Assertion Density per LoC"], bar_width, alpha=opacity, color='#1f77b4', label='Assertion Density per LoC')

# Setting the primary y-axis limits
ax1.set_ylim(0, max(data["Assertion Density per LoC"]) * 1.2)  # Extend range by 20%

# Create a second y-axis for "Assertion Density per Unit Test"
ax2 = ax1.twinx()
bars2 = ax2.bar(index + bar_width/2, data["Assertion Density per Unit Test"], bar_width, alpha=opacity, color='#ff7f0e', label='Assertion Density per Unit Test')

# Setting the secondary y-axis limits
ax2.set_ylim(0, max(data["Assertion Density per Unit Test"]) * 1.2)  # Extend range by 20%

# Setting the labels and titles
ax1.set_xlabel('Method')
ax1.set_ylabel('Assertion Density per LoC', color='#1f77b4')
ax2.set_ylabel('Assertion Density per Unit Test', color='#ff7f0e')
ax1.set_title('Assertion Metrics by Type and Row')
ax1.set_xticks(index)
ax1.set_xticklabels(rows)

# Improving legend placement
fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0), shadow=False, ncol=2)

# Render the plot
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the rectangle in tight_layout to leave space for the legend
plt.show()
