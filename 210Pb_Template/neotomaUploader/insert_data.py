import logging
from .pull_params import pull_params

def insert_data(cur, yml_dict, csv_template, uploader):
    data_query = """
                 SELECT ts.insertdata(_sampleid := %(sampleid)s,
                                      _variableid := %(variableid)s,
                                      _value := %(value)s)
                 """
    params = ['value']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.data')

    data_points = []
    counter = 0
    for i, val_dict in enumerate(inputs):
        val_dict['value'] = [None if item == 'NA' else item for item in val_dict['value']]
        for j, val in enumerate(val_dict['unitcolumn']):

            get_varid = """SELECT * FROM ndb.variableunits WHERE variableunits %% %(units)s;"""
            cur.execute(get_varid, {'units': val_dict['unitcolumn'][j]})
            varid = cur.fetchone()[0]

            cur.execute(data_query, {'sampleid': int(uploader['samples'][counter]),
                                    'variableid': int(varid),
                                    'value': val_dict['value'][i]})
        
            result = cur.fetchone()[0]
            counter +=1
            data_points.append(result)

    return data_points