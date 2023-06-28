import pandas as pd

def valid_column(yaml_vals):
    response = {'message': []}
    
    if dict1['type']=='number':
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            response['message'].append('✗ Site {column_name} is not properly formatted.')
    if dict1['type']=='string':
        if not pd.api.types.is_string_dtype(df[column_name]):
            response['message'].append('✗ Site {column_name} is not properly formatted.')
    if dict1['type']=='date':
        if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
            response['message'].append('✗ Site {column_name} is not properly formatted.')
    message = ' '.join(response['message'])

    return response['message']

def cleanColumn(df, dict1):
    column_name = dict1['column']
    if dict1['repeat']==True:
        column_vals = df[column_name].tolist()
    else:
        column_vals = list(df[column_name].unique())
    return column_vals

