import logging
from .pull_params import pull_params

def insert_dataset_pi(cur, yml_dict, csv_template, uploader):
    
    params = ['contactname']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.contacts')
    
    get_contact = """SELECT * FROM ndb.contacts WHERE contactname %% %(name)s;"""
    
    baseid = 1
    contids = []
    for i in inputs['contactname']:
        cur.execute(get_contact, {'name': i})
        contids.append({'name': i, 'id': cur.fetchone()[0], 'order': baseid})
        baseid = baseid + 1
    
    result = []
    for contact in contids:
        inserter = """SELECT ts.insertdatasetpi(_datasetid := %(datasetid)s, 
                                                _contactid := %(contid)s,
                                                _piorder := %(piorder)s);"""
        cur.execute(inserter, {'datasetid': int(uploader['datasetid']), 
                               'contid': int(contact['id']),
                               'piorder': int(contact['order'])})
        result.append(cur.fetchone()[0])

    return result