import yaml
from yaml.loader import SafeLoader
import pandas as pd

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

# Load the YAML file and flatten the dictionary
yml_file = 'template.yml'
with open(yml_file) as f:
    yml_data = yaml.load(f, Loader=SafeLoader)
flat_yml_data = flatten_dict(yml_data)

col_keys = [k for k in flat_yml_data.keys() if k.endswith('_column')]

# Get the corresponding values for the column keys
col_values = [flat_yml_data[k] for k in col_keys]
print(len(col_values))


# Load the spreadsheet file
csv_file = 'Bass 2005 SLBE.csv'
df = pd.read_csv(csv_file)
#df.columns = [col.replace('.', ' ') for col in df.columns]

print(len(df.columns))
#print("values not in columns")
print(sorted(set(col_values)-set(df.columns)))

#print("columns not in values")
print(sorted(set(df.columns)-set(col_values)))
# Compare the column names with the flattened YAML keys
if set(df.columns) == set(col_values):
    print("The column names and flattened YAML keys match")
else:
    print("The column names and flattened YAML keys do not match")