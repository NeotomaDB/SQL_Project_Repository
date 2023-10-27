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

    print(inputs)
    data_points = []
    for i, value in enumerate(inputs['unitcolumn']):
        get_varid = """SELECT * FROM ndb.variableunits WHERE variableunits %% %(units)s;"""
        cur.execute(get_varid, {'units': inputs['unitcolumn'][i]})
        varid = cur.fetchone()[0]

        cur.execute(data_query, {'sampleid': int(4), # int(uploader['sampleid']),
                                 'variableid': int(varid),
                                 'value': float(inputs['value'][i])})
    
        result = cur.fetchone()[0]
        data_points.append(result)

    return data_points