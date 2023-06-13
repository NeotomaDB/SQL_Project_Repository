import yaml
from yaml.loader import SafeLoader
from collections import defaultdict
import itertools
import pandas as pd
import os
import sys
import argparse
"""
To run from command line use:
python csvValidator.py /path/to/directory
Example:/
python 210Pb_Template/neotomaUploader/csvValidator.py --path=210Pb_Template/data/ --template=210Pb_Template/template.yml
"""

def ymlToDict(yml_file):
    with open(yml_file) as f:
        yml_data = yaml.load(f, Loader=SafeLoader)
    return yml_data

def getRequiredCols(dict1):
    data = dict1['metadata']
    required_cols = [d['column'] for d in data if d['required']==True]
    return required_cols

def vocabDict(dict1):
    """
    Obtain the units dictionary
    """
    # Todo raise statement if the dictionary does not have a 'metadata' key
    data = dict1['metadata']
    vocab_dict = {d['type']: d['vocab'] for d in data if d['vocab'] is not None}

    unit_cols = defaultdict(list)
    for d in data:
        if 'type' in d.keys():
            unit_cols[d['type']].append(d['column'])
    unit_cols = dict(unit_cols)

    return unit_cols, vocab_dict

def csvValidator(filename, units, dict1):
    log_file = []

    # Take directly from .yml file
    data = dict1['metadata']
    col_values = [d['column'] for d in data]

    #col_values = list(itertools.chain.from_iterable(unitcols.values()))

    # Obtain the restricted vocabulary
    #unit_cols, vocab_dict = vocabDict(dict1=dict1)

    try:
        # Load csv file as data frame and extract columns
        df = pd.read_csv(filename)
        # Verify that all columns are contained in the YAML file
        diff_col = sorted(set(col_values)-set(list(df.columns)))

        # Verify that all columns from the YAML are in the data frame
        diff_val = sorted(set(list(df.columns))-set(col_values))

        # Report in the log
        if diff_col == diff_val:
            message = ["✔  The column names and flattened YAML keys match"]
            log_file = log_file + message
        else:
            log_file = log_file +["✗  The column names and flattened YAML keys do not match"]
            log_file = log_file +[f"Columns from the YAML template are not in the data frame: '{diff_val}'"]
            log_file = log_file +[f"Columns from the data frame not in the YAML template: '{diff_col}'"]

        # Guarantee that the keys in the controled vocabulary matched with the allowed terms
        for key, values in units.items():
            if key in df.columns:
                column_values = df[key].tolist()
                all_values_in_dict = all(value in values for value in column_values)
            
                if all_values_in_dict:
                    log_file.append(f"✔  All values in the '{key}' column correspond to the vocabulary."+ '\n')
                else:
                    log_file.append(f"✗  Not all values in the '{key}' column correspond to the vocabulary."+ '\n')

    except Exception as e:
        log_file.append(f"✗  Error opening file '{filename}': {e}"+ '\n')

    return log_file