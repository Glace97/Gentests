import pandas as pd
import matplotlib.pyplot as plt

# Incorrect tests
# Num of compiling tests: 1971
#'''
data = {
    'Test Suite': ['V1 GPT3.5-turbo-16k', 'V2 GPT3.5-turbo-16k', 'V2 GPT4'],
    'AssertionFailedError': [184, 87, 96],
    'Throws java.lang exception': [10, 11, 10],
    'Mockito Exceptions': [0, 40, 16],
}
#'''

# Non compiling teests
# Num of all tests: 2501
'''
data = {
    'Test Suite': ['V1 GPT3.5-turbo-16k', 'V2 GPT3.5-turbo-16k', 'V2 GPT4'],
    'Cannot Resolve Method': [5,13, 11],  # Ambigious method call more common in cases of polymorphism
    'Ambigious Method call': [5, 15, 13],
    'Incompatible types: cannot be converted': [0, 8, 1],
    'Method in class cannot be applied to given types': [1, 15, 1]
}

'''

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data)

# Set the 'Test Suite' column as index
df.set_index('Test Suite', inplace=True)

# Plot a stacked bar chart
ax = df.plot(kind='bar', stacked=True, figsize=(10, 7))

# Rotate x-axis labels
plt.xticks(rotation=0, ha='center')


# Adding titles and labels
plt.title('Failing tests')
#plt.title('Non-compiling tests')

#plt.xlabel('Test Suite')
plt.ylabel('Number of Failures')

# Show legend
plt.legend(title='Error Types')

# Display the plot
plt.show()
