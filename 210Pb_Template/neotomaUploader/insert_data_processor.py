import logging
from .pull_params import pull_params

def insert_data_processor(cur, yml_dict, csv_template, uploader):
 
    params = ['contactid']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.sampleanalysts')

    get_contact = """SELECT * FROM ndb.contacts WHERE contactname %% %(name)s;"""

    contids = list()
    for i in inputs['contactid']:
        cur.execute(get_contact, {'name': i})
        contids.append({'name': i, 'id': cur.fetchone()[0]})

    results = []
    for contact in contids:
        processor = """SELECT ts.insertdataprocessor(_datasetid := %(datasetid)s,
                                                     _contactid := %(contactid)s)"""
        cur.execute(processor, {'datasetid': int(uploader['datasetid']), 
                                'contactid': int(contact['id'])})
        results.append(cur.fetchone()[0])
    return None