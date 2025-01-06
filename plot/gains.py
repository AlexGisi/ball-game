import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse


# Custom cost for each step
# ACTION_DELTA_WEIGHT = 1e2
# ERROR_WEIGHT = 1e-3

ACTION_DELTA_WEIGHT = 1e2
ERROR_WEIGHT = 1e-3

# Set the directory containing the subdirectories
parser = argparse.ArgumentParser()
parser.add_argument('directory')
args = parser.parse_args()

directory = args.directory

# Get subdirectories whose names can be converted to float values
subdirs = []
for d in os.listdir(directory):
    full_path = os.path.join(directory, d)
    if os.path.isdir(full_path):
        try:
            float(d)  # Check if directory name can be parsed as float
            subdirs.append(d)
        except ValueError:
            # If not float, ignore this directory
            print(f"ignored directory {d}")

# Sort subdirs by their float value
subdirs = sorted(subdirs, key=lambda x: float(x))

# Load each dataframe into a dictionary keyed by the float value of the directory name
df_dict = {}
for d in subdirs:
    data_path = os.path.join(directory, d, "data.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df_dict[float(d)] = df
    else:
        print(f"path does not exist: {data_path}")

# For each dataframe:
# 1. Group by 'episode'
# 2. Calculate the average cost for each episode
# 3. Collect these average costs into a list for box plotting
boxplot_data = []
labels = []

for name, df in df_dict.items():
    df['error'] = df['reference_y'] - df['ball_y']
    df['action_delta'] = df['action'].diff()

    # Custom cost
    # df['cost_custom'] = df['cost']
    df['cost_custom'] = df['action_delta']**2 * ACTION_DELTA_WEIGHT + df['error']**2 * ERROR_WEIGHT

    avg_cost_by_episode = df.groupby('episode')['cost_custom'].mean()  # Series of avg cost per episode
    boxplot_data.append(avg_cost_by_episode.values)
    labels.append(str(name))

# Create a figure and a set of axes for the boxplots
fig, ax = plt.subplots(figsize=(10, 6))

# Create the boxplots
ax.boxplot(boxplot_data, labels=labels)

# Set axis labels and title
ax.set_xlabel("gain")
ax.set_ylabel("mean episode cost")
ax.set_title(f"mean episode costs for different gains (control derivative weight={ACTION_DELTA_WEIGHT}, error weight={ERROR_WEIGHT})")

# Display the figure
plt.tight_layout()
plt.show()
