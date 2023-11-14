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
python csv_validator.py /path/to/directory
Example:/
python 210Pb_Template/neotomaUploader/csvValidator.py --path=210Pb_Template/data/ --template=210Pb_Template/template.yml
"""

def yml_to_dict(yml_file):
    """_Read in valid yaml file._

    Args:
        yml_file (_string_): _A valid filename for a yaml file._

    Returns:
        _dict_: _A dict representation of a yaml file._
    """
    if not os.path.isfile(yml_file):
        raise FileNotFoundError(f"The file '{yml_file}' could not be found within the current path.")

    with open(yml_file, encoding = "UTF-8") as file:
        yml_data = yaml.load(file, Loader = SafeLoader)
    return yml_data


def csv_validator(filename, yml_data):
    """_Validate csv file for use in the validator._

    Args:
        filename (_string_): _A valid csv filename._
        yml_data (_dict_): _A dict passed from yml_to_dict()_

    Returns:
        _type_: _description_
    """
    log_file = []
    # Take directly from .yml file
    col_values = [d.get('column') for d in yml_data]

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"The file '{filename}' could not be found within the current path.")

    try:
        # Load csv file as data frame and extract columns
        df = pd.read_csv(filename)
    except pd.errors.ParserError:
        log_file.append(f"✗  Error opening file '{filename}': {e}"+ '\n')    

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

    return log_file
