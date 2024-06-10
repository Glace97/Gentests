import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


### DATA COMPILATION RATE###
# Full data set compilation rate
'''
methods = ['Randoop', 'V1 GPT3.5-turbo-16k', 'Human-written']
ratios = [1379/1416, 6235/9434, 4195/4195]  
'''
# Subset of the data compilation rate
#methods = ['V1 GPT3.5-turbo-16k', 'V2 GPT3.5-turbo-16k', 'V2 GPT4']
#ratios = [1971/2501, 1971/2162, 1673/1725]  # Actual ratios based on your values


### DATA FAILING/CORRECT TESTS ####
'''
methods = ['Randoop', 'V1 GPT3.5-turbo-16k', 'Human-written']
ratios = [0, 530/2501, 0]  # Actual ratios based on your values
'''
# Subset of the data pass/fail rate
#'''
methods = ['V1 GPT3.5-turbo-16k', 'V2 GPT3.5-turbo-16k', 'V2 GPT4']
#ratios = [530/2501, 148/1971, 111/1673]  #Fail rate
ratios = [1774/1971, 1823/1971, 1562/1673]
#'''


# Creating the bar chart
plt.figure(figsize=(8, 4))  # Size of the figure
plt.bar(methods, ratios, color=['#1f77b4', '#72b754', '#ef5050'])

# Adding titles and labels
plt.title('Percentage of correct tests')
#plt.title('Percentage of Compiling Tests')

plt.xlabel('Method')

plt.ylabel('Correct tests (%)')
#plt.ylabel('Compiling (%)')

# Set the y-axis to display percentage
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

# Setting the y-axis limit slightly above the maximum ratio to prevent the line from cutting through the displayed ratios
plt.ylim(0, max(ratios) + 0.1)

# Remove the top line (spine) of the plot for a cleaner look
plt.gca().spines['top'].set_visible(False)

# Adding the ratio values above the bars for clarity
for i, ratio in enumerate(ratios):
    plt.text(i, ratio + 0.02, f'{ratio:.2%}', ha = 'center', color = 'black')

# Show the plot
plt.show()

# Clear cache
plt.clf()
plt.cla()
plt.close()