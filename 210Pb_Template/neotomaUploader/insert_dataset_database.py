
import logging
from .pull_params import pull_params

def insert_dataset_database(cur, yml_dict, uploader):
    db_query = """
        SELECT ts.insertdatasetdatabase(_datasetid := %(datasetid)s, 
                                        _databaseid := %(databaseid)s)
               """
    # Put it in the XLXs
    databaseid = yml_dict['databaseid']

    cur.execute(db_query, {'datasetid': int(uploader['datasetid']), 
                           'databaseid': int(databaseid)})
    result = cur.fetchone()[0]
    
    return result