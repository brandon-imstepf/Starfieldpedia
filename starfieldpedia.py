import os
import json
import pandas as pd
from tkinter import Tk, messagebox, ttk

def lowercase_keys(input_dict):
    """Recursively convert all keys in dictionary to lowercase."""
    if not isinstance(input_dict, dict):
        return input_dict

    return {k.lower(): lowercase_keys(v) for k, v in input_dict.items()}

def load_resources():
    """Load organic and inorganic resources."""
    with open("Resources/organic_resources.json", 'r') as org_file:
        organic_resources = json.load(org_file)

    with open("Resources/inorganic_resources.json", 'r') as inorg_file:
        inorganic_resources = json.load(inorg_file)

    return {**organic_resources, **inorganic_resources}

# Load resource details
resources_dict = load_resources()

def on_planet_selected(event):
    """Handle planet selection in the Treeview."""
    item = tree.selection()[0]  # get selected item
    
    planet_name = tree.item(item)["values"][0]
    
    # If the selected item is not in the dataframe, return early
    if planet_name not in df['name'].values:
        return

    # Check if the selected item has children already
    if tree.get_children(item):
        # If it has children (i.e., details have been previously loaded), remove them
        for child in tree.get_children(item):
            tree.delete(child)
    else:
        # First, insert the sub-headers for resources
        tree.insert(item, "end", text="", values=("Resource Name", "Element", "Rarity", "State", "Weight", "Value"))
        
        # Fetch resources for the planet
        planet_data = tree.item(item)["values"]
        planet_name = planet_data[0]
        planet_row = df[df['name'] == planet_name].iloc[0]
        resources = planet_row['resources']

        # Extract resource names based on 'true' values
        available_resources = [resource for resource, available in resources.items() if available]

        # Insert the resource details beneath the sub-headers
        for resource in available_resources:
            resource_details = resources_dict.get(resource, {})
            details_values = (resource, 
                              resource_details.get("element_name", ""), 
                              resource_details.get("rarity", ""),
                              resource_details.get("state_of_matter", ""),
                              resource_details.get("weight", ""),
                              resource_details.get("value", ""))
            tree.insert(item, "end", text="", values=details_values)


def filter_planets_by_resource(resource_name):
    """Filter planets by the selected resource."""
    tree.delete(*tree.get_children())  # Clear the current tree view
    filtered_data = df[df['resources'].apply(lambda x: x.get(resource_name, False))]

    for _, row in filtered_data.iterrows():
        tree.insert("", "end", values=(row['name'], row.get('type', ''), row.get('gravity', ''), row.get('temperature', ''), row.get('atmosphere', ''), row.get('magnetosphere', '')))

def reset_planet_view():
    """Reset the planet view to show all planets."""
    tree.delete(*tree.get_children())  # Clear the current tree view
    for _, row in df.iterrows():
        tree.insert("", "end", values=(row['name'], row.get('type', ''), row.get('gravity', ''), row.get('temperature', ''), row.get('atmosphere', ''), row.get('magnetosphere', '')))



# Load data from all JSON files within the "systems" directory
data = []
systems_directory = 'systems'

for file in os.listdir(systems_directory):
    if file.endswith(".json"):
        filepath = os.path.join(systems_directory, file)
        with open(filepath, 'r') as f:
            try:
                content_json = json.loads(f.read())
                content_json = lowercase_keys(content_json)
                for system_data in content_json['systems']:
                    for planet in system_data['planets']:
                        # Extract resources from fauna and flora
                        fauna_resources = {res: True for fauna in planet.get('fauna', []) for res, val in fauna.get('resources', {}).items() if val}
                        flora_resources = {res: True for flora in planet.get('flora', []) for res, val in flora.get('resources', {}).items() if val}

                        # Merge these with main resources
                        merged_resources = {**planet['resources'], **fauna_resources, **flora_resources}
                        planet['resources'] = merged_resources

                        data.append(planet)
            except (json.JSONDecodeError, KeyError):
                # Here, you might want to print the error and/or the file content for debugging
                continue

df = pd.DataFrame(data)

# Create tkinter window
root = Tk()
root.title("Planet Details")
root.geometry("800x400")



# Create and configure Treeview with Scrollbar
frame = ttk.Frame(root)
frame.pack(pady=20, padx=20)

tree = ttk.Treeview(frame, columns=('Name', 'Type', 'Gravity', 'Temperature', 'Atmosphere', 'Magnetosphere'), show='headings')
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=120)
    
# Populate Treeview with planet data
for _, row in df.iterrows():
    tree.insert("", "end", values=(row['name'], row.get('type', ''), row.get('gravity', ''), row.get('temperature', ''), row.get('atmosphere', ''), row.get('magnetosphere', '')))

tree.bind("<Double-1>", on_planet_selected)  # Bind double click event

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tree.pack(fill="both", expand=True)

# Creating a Frame for resource buttons on the left side
button_frame = ttk.Frame(root)
button_frame.pack(side="left", fill="y", padx=10)

# Generate buttons for each resource in a grid layout
columns = 6
for idx, resource in enumerate(resources_dict.keys()):
    row = idx // columns
    col = idx % columns
    ttk.Button(button_frame, text=resource, command=lambda res=resource: filter_planets_by_resource(res)).grid(row=row, column=col, sticky="w", padx=5, pady=5)

# Add a reset button below the grid
ttk.Button(button_frame, text="Reset", command=reset_planet_view).grid(row=row+1, columnspan=columns, pady=20)

root.mainloop()
