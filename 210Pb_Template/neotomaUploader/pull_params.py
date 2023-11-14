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
        _dict_: _cleaned and repeated valors for input into a Tilia insert function._
    """
    add_unit_inputs = {}
    if re.match('.*\.$', table) == None:
        table = table + '.'
    add_units_inputs_list=[]
    for i in params:
        valor = retrieve_dict(yml_dict, table + i)
        if len(valor) > 0:
            for count, val in enumerate(valor):
                new_dict = {}
                clean_valor = clean_column(val.get('column'),
                                        csv_template,
                                        clean = not val.get('rowwise'))
                if len(clean_valor) > 0:
                    match val.get('type'):
                        case "string":
                            clean_valor = list(map(str, clean_valor))
                        case "date":
                            #clean_valor = list(map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(), chain(*clean_valor)))
                            clean_valor = list(map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(), clean_valor))
                        case "int":
                            clean_valor = list(map(int, clean_valor[0]))
                        case "float":
                            clean_valor = list(map(float, clean_valor[0]))
                        case "coordinates (latlong)":
                            clean_valor = [float(num) for num in clean_valor[0].split(',')]
                add_unit_inputs[i] = clean_valor
                if 'unitcolumn' in val:
                    clean_valor2 = clean_column(val.get('unitcolumn'),
                                            csv_template,
                                            clean = not val.get('rowwise'))
                    add_unit_inputs['unitcolumn'] = clean_valor2
            
                if 'uncertainty' in val.keys():
                    clean_valor3 = clean_column(val['uncertainty']['uncertaintycolumn'],
                                                csv_template,
                                                clean = not val.get('rowwise'))
                    add_unit_inputs['uncertainty'] = clean_valor3
                
                samples_dict = add_unit_inputs.copy()
                samples_dict['name'] = val.get('column')
                samples_dict['taxonid'] = val.get('taxonid')
                samples_dict['taxonname'] = val.get('taxonname')
                add_units_inputs_list.append(samples_dict)

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

    if params == ['value']:
        return add_units_inputs_list
    else:
        return add_unit_inputs