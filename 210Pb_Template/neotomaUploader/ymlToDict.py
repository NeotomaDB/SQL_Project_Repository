import yaml
from yaml.loader import SafeLoader
from collections import defaultdict
import json
import sys
#args = sys.argv
#file = args[1]

def ymlToDict(yml_file):
    '''
    Convert a Pb210 template yml file into a dictionary.
    Parameters: 
        yml_file
    Returns:
        dictionary
    Example:
        ymlToDict('template.yml')
    '''
    with open(yml_file) as f:
        data = yaml.load(f, Loader=SafeLoader)

    # Getting the name of the columns from YML
    column_names = [sub['column'] for sub in data['metadata']]

    # Getting the dictionaries that have a 'type' attribute associated
    # to them
    type_dicts = [dict1 for dict1 in data['metadata'] 
                if 'type' in dict1.keys()]

    # Extraction of k, v for the dictionary
    type_names = [sub['type'] for sub in type_dicts]
    col_names = [sub['column'] for sub in type_dicts]

    # Building the dictionary:
    type_dict = defaultdict(list)

    for k, v in zip(type_names, col_names):
        type_dict[k].append(v)

    # Getting the dictionaries that contain units
    unit_dicts = [dict1 for dict1 in data['metadata'] 
                if 'units' in dict1.keys()]

    ## Retrieve column names from the selected dictionaries
    unit_cols = [sub['units'][0] for sub in unit_dicts]

    type_names = [sub['type'] for sub in unit_cols]
    col_names = [sub['column'] for sub in unit_cols]

    units_dict = defaultdict(list)
    for k, v in zip(type_names, col_names):
        units_dict[k].append(v)

    # Adding the dictionaries
    type_dict.update(units_dict)
    type_dict = dict(type_dict)

    return type_dict