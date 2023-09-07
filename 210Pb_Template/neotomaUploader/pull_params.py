import datetime
import re
from itertools import chain
from .retrieve_dict import retrieve_dict
from .clean_column import clean_column

def pull_params(params, yml_dict, csv_template, table):
    """_Pull parameters associated with an insert statement from the yml/csv tables._

    Args:
        params (_list_): _A list of strings for the columns needed to generate the insert statement._
        yml_dict (_dict_): _A `dict` returned by the YAML template._
        csv_template (_dict_): _The csv file with the required data to be uploaded._
        table (_string_): _The name of the table the parameters are being drawn for._

    Returns:
        _dict_: _cleaned and repeated values for input into a Tilia insert function._
    """
    add_unit_inputs = {}
    if re.match('.*\.$', table) == None:
        table = table + '.'
    for i in params:
        value = retrieve_dict(yml_dict, table + i)
        if len(value) > 0:
            for count, val in enumerate(value):
                clean_value = [clean_column(val.get('column'),
                                        csv_template,
                                        clean = not val.get('repeat'))]
                if len(clean_value) > 0:
                    match value[count].get('type'):
                        case "string":
                            clean_value = list(map(str, chain(*clean_value)))
                        case "date":
                            clean_value = list(map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(), chain(*clean_value)))
                        case "int":
                            clean_value = list(map(int, clean_value[0]))
                        case "float":
                            clean_value = list(map(float, clean_value[0]))
                        case "coordinates (latlong)":
                            clean_value = [[float(i) for i in clean_value[0][0].split(',')]]
            add_unit_inputs[i] = clean_value
        else:
            add_unit_inputs[i] = []
    maxlen = 0
    for i in params:
        if len(add_unit_inputs.get(i)) > maxlen:
            maxlen = len(add_unit_inputs.get(i))
    for i in params:
        if len(add_unit_inputs.get(i)) == 0:
            add_unit_inputs[i] = [None for j in range(maxlen)]
        elif len(add_unit_inputs.get(i)) == 1:
            add_unit_inputs[i] = [add_unit_inputs[i][0] for j in range(maxlen)]
    return add_unit_inputs