import pandas as pd
import yaml

def csv_to_yaml(xl_path, yml_output= 'output_yml.yml'):
    """
    _csv_to_yaml_

    Args:
        xl_path (_list_): _Excel file to be used as template_
        yml_output (_list_): _Location and file name where the yaml template will be stored_

    Returns:
        _None_: _The output file will be stored, no need to return anything here_
    """
    df = pd.read_excel(xl_path)

    # Convert DataFrame to a dictionary with list of columns
    data_dict = df.to_dict(orient='records')
    nested_data = [{key: value for key, value in zip(df.columns, row)} for row in data_dict]

    with open(yml_output, 'w') as yaml_file:
        yaml.dump(nested_data, yaml_file, default_flow_style=False)

    print(f'YAML file stored in {yml_output} successfully.')

    return None