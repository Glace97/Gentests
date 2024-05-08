import matplotlib.pyplot as plt

# Define the data for the plot
rows = ["Randoop", "V1 gpt3.5-turbo-16k", "Manual"]
values = [0, 484, 1553]

# Create a bar chart
plt.figure(figsize=(8, 6))  # Set the figure size
plt.bar(rows, values, color=['#1f77b4', '#72b754', '#ef5050'])  # Create bars with blue color

# Add titles and labels
plt.title('Checks against Crashes')  # Title of the chart
plt.xlabel('Method')  # Label for the x-axis
plt.ylabel('Number of Checks')  # Label for the y-axis

# Display the plot
plt.show()
