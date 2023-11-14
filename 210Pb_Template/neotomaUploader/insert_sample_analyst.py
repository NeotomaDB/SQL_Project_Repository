import logging
from .pull_params import pull_params

def insert_sample_analyst(cur, yml_dict, csv_template, uploader):
    """
    """
    
    params = ['contactid']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.sampleanalysts')
    get_contact = """SELECT * FROM ndb.contacts WHERE contactname %% %(contactname)s;"""
    
    contids = []
    baseid = 1
    for i in inputs['contactid']:
        cur.execute(get_contact, {'contactname': i})
        contids.append({'contactname': i, 'id': cur.fetchone()[0], 'order': baseid})
        baseid = baseid + 1
    
    result = []
    counter = 0
    for i in range(len(uploader['samples'])):
        for contact in contids:
            inserter = """
                        SELECT ts.insertsampleanalyst(_sampleid := %(sampleid)s,
                                                    _contactid := %(contactid)s,
                                                    _analystorder := %(analystorder)s)
                    """
            cur.execute(inserter, {'sampleid': int(uploader['samples'][counter]), 
                                'contactid': int(contact['id']),
                                'analystorder': int(contact['order'])})
            result.append(cur.fetchone()[0])
            counter += 1

    return result