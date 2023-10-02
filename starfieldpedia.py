import os
import json
import pandas as pd
from tkinter import Tk, Listbox


def lowercase_keys(input_dict):
    """
    Recursively convert all keys in dictionary to lowercase.
    """
    if not isinstance(input_dict, dict):
        return input_dict

    lowercased_dict = {}
    for k, v in input_dict.items():
        if isinstance(v, dict):
            v = lowercase_keys(v)
        elif isinstance(v, list):
            v = [lowercase_keys(item) if isinstance(item, dict) else item for item in v]
        lowercased_dict[k.lower()] = v
    return lowercased_dict


# Load data from all JSON files within the "systems" directory
data = []
systems_directory = 'systems'

for file in os.listdir(systems_directory):
    if file.endswith(".json"):
        filepath = os.path.join(systems_directory, file)
        print(f"Processing file: {filepath}")  # Printing the filename
        with open(filepath, 'r') as f:
            content = f.read()
            try:
                content_json = json.loads(content)
                content_json = lowercase_keys(content_json)
                for system_data in content_json['systems']:
                    data.extend(system_data['planets'])
            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {filepath}")
                print(content)  # Printing the content of the problematic file
                continue  # Skip this file and move to the next one
            except KeyError:
                print(f"KeyError encountered in file: {filepath}")
                print(content)  # Print the content of the file causing the KeyError
                continue

# Convert data to DataFrame
try:
    df = pd.DataFrame(data)
except Exception as e:
    print(f"Error while converting data to DataFrame: {e}")
    print(data)  # Print the content of 'data' to check for issues

# Create a simple tkinter window to display planet names
root = Tk()
root.title("Planet List")
root.geometry("300x400")

# Add planet names to a listbox
listbox = Listbox(root)
try:
    for planet_name in df['name'].tolist():
        listbox.insert("end", planet_name)
except KeyError:
    print("KeyError encountered while populating listbox.")
    print(df.head())  # Print the first few rows of the DataFrame to inspect it

listbox.pack(pady=20)

root.mainloop()
