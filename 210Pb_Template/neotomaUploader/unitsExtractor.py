### Creating the new units dict
import pandas as pd
from ymlToDict import ymlToDict

def unitsExtractor(template, file):
    """
    Function to return reported units in the spreadsheets
    Input: 
        .csv file
    Returns: 
        dictionary with all the required validation units
    Example:
        unitsExtractor('template.yml', 'Bass 2005 SLBE.csv')
    """
    yml_dict = ymlToDict(template)
    data=pd.read_csv(file)

    elements = ['ddunits','cdmunits', 'riunits', 'accum',
                'timeunits', 'precision', 'model', 'estimate',
                'position']
    
    units_dict = dict()

    for element in elements:
        for column in yml_dict[element]:
            if column in data.columns:
                value = data[column].unique().tolist()
                if element in units_dict.keys():
                    units_dict[element] + value
                else:
                    units_dict[element] = value

    return units_dict