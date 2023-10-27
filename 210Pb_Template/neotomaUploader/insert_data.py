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

    #print(inputs)
    #print("uploader sampleid")
    #print(uploader['samples'])
    data_points = []
    counter = 0
    for i, val_dict in enumerate(inputs):
        counter +=1
        print(val_dict)
        for j, val in enumerate(val_dict['unitcolumn']):
            counter +=1

            get_varid = """SELECT * FROM ndb.variableunits WHERE variableunits %% %(units)s;"""
            cur.execute(get_varid, {'units': val_dict['unitcolumn'][j]})
            varid = cur.fetchone()[0]

            cur.execute(data_query, {'sampleid': int(4), # int(uploader['sampleid']),
                                    'variableid': int(varid),
                                    'value': float(val_dict['value'][i])})
        
            result = cur.fetchone()[0]
            data_points.append(result)
    print(len(counter))
    print(len(uploader['samples']))

    return data_points