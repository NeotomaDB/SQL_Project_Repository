import logging
from .pull_params import pull_params

def insert_sample_analyst(cur, yml_dict, csv_template, uploader):
    """
    """
    
    params = ['contactid']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.sampleanalysts')
    
    get_contact = """SELECT * FROM ndb.contacts WHERE contactname %% %(contactname)s;"""
    
    cur.execute(get_contact, {'contactname': inputs['contactid'][0]})
    contactid = cur.fetchone()[0]

    return contactid