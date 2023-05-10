import yaml
from yaml.loader import SafeLoader
import pandas as pd
import os
import sys
import argparse
"""
To run from command line use:
python csvValidator.py /path/to/directory
Example:/
python csvValidator.py --path=/data --template=/210Pb_Template/template.yml
"""
# Obtain arguments and parse them to handle command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to the directory')
parser.add_argument('--template', type=str, help='Template to use for evaluation')
args = parser.parse_args()

# directory argument
if not args.path:
    print('Specify a directory path using the --path argument')
    sys.exit(1)
directory = args.path

if not args.template:
    print('Specify a template path using the --template argument')
    sys.exit(1)
yml_file = args.template

# Leave just in case we use a nested YAML
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                sub_items = flatten_dict(item, f"{new_key}{sep}{i}", 
                                         sep=sep).items()
                items.extend([(f"{k}{sep}{sub_key}", sub_value) 
                              for sub_key, sub_value in sub_items])
        else:
            items.append((new_key, v))
    return dict(items)

# Load the yml obtained from the argsparser
with open(yml_file) as f:
    yml_data = yaml.load(f, Loader=SafeLoader)
flat_yml_data = flatten_dict(yml_data) # OK to remove for now, reconsider if we use a nested YAML 

col_keys = [k for k in flat_yml_data.keys() if k.endswith('_column')]

# Get the corresponding values for the column keys
col_values = [flat_yml_data[k] for k in col_keys]

# Open a log file
with open('application.log', 'w', encoding = "utf-8") as log_file:
    # Iterate over the directory's files
    for filename in os.listdir(directory):
        # Some files have a .log hidden extension
        root, ext = os.path.splitext(filename)
        # To avoid .csv being removed
        if ext == ".csv":
            filename = root+ext
        else:
            filename = root
        log_file.write(filename + '\n')

        try:
            df = pd.read_csv(os.path.join(directory, filename))
            length = len(df.columns)
            # log_file.write(f'Number of columns is: {length}'+'\n')
            
            diff_col = sorted(set(col_values)-set(df.columns))
            diff_val = sorted(set(df.columns)-set(col_values))
 
            # Compare the column names with the flattened YAML keys
            if set(df.columns) == set(col_values):
                log_file.write("✔  The column names and flattened YAML keys match"+ '\n')
            else:
                log_file.write("✗  The column names and flattened YAML keys do not match"+ '\n')
                log_file.write(f"Columns not in values: '{diff_val}'"+ '\n')
                log_file.write(f"Values not in columns: '{diff_col}'"+ '\n')
        
        except Exception as e:
            log_file.write(f"✗  Error opening file '{root}': {e}"+ '\n')

# To Do: Consider using glob
# Question: How many log files? Should it be a logfile for csv file?
# Question: Why do some files seem to have a hidden `.log` extension?
# Question: Nested or not nested YAML?