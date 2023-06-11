import pandas as pd
from difflib import get_close_matches

# Load data from CSV files
df1 = pd.read_csv('data/file1.csv')
df2 = pd.read_csv('data/file2.csv')

# Function to find close matches in the names
def match_name(name):
    matches = get_close_matches(name, df2['player_name'], n=1, cutoff=0.8)
    if matches:
        return df2[df2['player_name'] == matches[0]]['tp_id'].values[0]
    else:
        return None

# Apply function to 'name' column
df1['tp_id'] = df1['name'].apply(match_name)

# Save the merged data to a new CSV file
df1.to_csv('data/merged.csv', index=False)