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

def csvValidator(filename, yml_data):
    log_file = []
    # Take directly from .yml file
    col_values = [d.get('column') for d in yml_data]

    try:
        # Load csv file as data frame and extract columns
        df = pd.read_csv(filename)
        df_columns = list(df.columns)
        # Verify that all columns from the DF are in the YAML file
        diff_col = sorted(set(col_values) - set(df_columns))

        # Verify that all columns from the YAML are in the DF
        diff_val = sorted(set(df_columns)-set(col_values))

        # Report in the log
        if diff_col == diff_val:
            message = ["✔  The column names and flattened YAML keys match"]
            log_file = log_file + message
        else:
            log_file = log_file + ["✗  The column names and flattened YAML keys do not match"]
            log_file = log_file + [f"Columns from the YAML template are not in the data frame: '{diff_val}'"]
            log_file = log_file + [f"Columns from the data frame not in the YAML template: '{diff_col}'"]

    except Exception as e:
        log_file.append(f"✗  Error opening file '{filename}': {e}"+ '\n')

    return log_file
