import pandas as pd
import ast
import tkinter as tk
from tkinter import filedialog
import os

# Create the tkinter window
root = tk.Tk()
root.withdraw()

### Step 1: Ask the user to select a csv file
csv_file_path = filedialog.askopenfilename(title="Select the CSV file", filetypes=[("CSV files", "*.csv")])

# If no file selected, stop the code
if not csv_file_path:
    print("No file selected. Action terminated.")
    exit()

# Load the CSV into pandas DataFrame
df = pd.read_csv(csv_file_path)

### Step 2: Get the column containing data in JSON format
json_column_name = 'Custom Fields'

# Validate that the column name exists in the pandas DataFrame
if json_column_name not in df.columns:
    print(f"Column '{json_column_name}' not found in the DataFrame. Exiting.")
    exit()

### Step 3: Convert the string representation of list of dictionaries into actual list
df[json_column_name] = df[json_column_name].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

### Step 4: Explode the list of dictionaries into separate rows
df_exploded = df.explode(json_column_name)

### Step 5: Extract 'values' and 'name' into separate columns
df_exploded['values'] = df_exploded[json_column_name].apply(lambda x: x['values'][0] if x and 'values' in x else '')
df_exploded['name'] = df_exploded[json_column_name].apply(lambda x: x['name'] if x and 'name' in x else '')

### Step 6: Pivot the DataFrame to get the desired result
df_pivoted = df_exploded.pivot_table(index=df_exploded.index, columns='name', values='values', aggfunc='first')

### Step 7: Concatenate the pivoted DataFrame with the original DataFrame
df_fixed = pd.concat([df, df_pivoted], axis=1)

### Step 8: Remove the original JSON type column
df_fixed = df_fixed.drop(columns=[json_column_name])

### Step 9: Save the fixed DataFrame to a new CSV file
output_csv_path = 'Modified_' + os.path.basename(csv_file_path)
output_full_path = os.path.join(os.path.dirname(csv_file_path), output_csv_path)
df_fixed.to_csv(output_full_path, index=False)

# Print the full path of the fixed CSV file
print(f"The modified file has been saved here: {output_full_path}")
