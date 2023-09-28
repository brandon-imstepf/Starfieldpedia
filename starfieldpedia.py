# Brandon Imstepf
# bimstepf1@gmail.com

"""
The goal of this program is, given all systems and their respective
planets in Bethesda Softwork's video game Starfield, find the optimal
system to build your outposts in to minimize Helium-3 Cargo Link usage.

Also to serve as a source of information for Starfield's many plaents.

"""

import os
import json
import tkinter as tk
import glob

def load_json_from_file(directory, filename):
    with open(os.path.join(directory, filename), 'r') as file:
        data = json.load(file)
    return data

# Example Usage
system_data = load_json_from_file("systems", "tau_ceti.json")
print(system_data)

def load_all_json_from_directory(directory):
    all_data = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_data = load_json_from_file(directory, filename)
            all_data.append(file_data)
            
    return all_data

# Example Usage
all_system_data = load_all_json_from_directory("systems")
print(all_system_data)