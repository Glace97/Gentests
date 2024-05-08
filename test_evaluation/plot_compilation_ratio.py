import matplotlib.pyplot as plt

# Data
methods = ['Randoop', 'V1 gpt3.5-turbo-16k', 'Human-written']
ratios = [1379/1416, 6235/9434, 4195/4195]  # Actual ratios based on your values

# Creating the bar chart
plt.figure(figsize=(8, 4))  # Size of the figure
plt.bar(methods, ratios, color=['#1f77b4', '#72b754', '#ef5050'])

# Adding titles and labels
plt.title('Compiling Tests Ratio')
plt.xlabel('Method')
plt.ylabel('Compiling Tests Ratio')


# Setting the y-axis limit slightly above 1 to prevent the line from cutting through the displayed ratios
plt.ylim(0, 1.05)

# Remove the top line (spine) of the plot for a cleaner look
plt.gca().spines['top'].set_visible(False)

# Adding the ratio values above the bars for clarity
for i, ratio in enumerate(ratios):
    plt.text(i, ratio + 0.02, f'{ratio:.4f}', ha = 'center', color = 'black')

# Show the plot
plt.show()
