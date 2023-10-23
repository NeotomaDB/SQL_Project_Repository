import logging
from .pull_params import pull_params

def insert_dataset (cur, yml_dict, csv_template, uploader):
        #cur, collunitid, datasetname):
    dataset_query = """SELECT ts.insertdataset(_collectionunitid:= %(collunitid)s,
                                               _datasettypeid := %(datasettypeid)s,
                                               _datasetname := %(datasetname)s);"""

    params = ['datasetname', 'datasettypeid']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.datasets')
    
    inputs = dict(map(lambda item: (item[0], None if all([i is None for i in item[1]]) else item[1]),
                      inputs.items()))
    
    cur.execute(dataset_query, {'collunitid': int(uploader['collunitid']),
                                'datasettypeid': int(5), #inputs['datasettypeid'],
                                'datasetname': inputs['datasetname']})
    datasetid = cur.fetchone()[0]
    return datasetid
