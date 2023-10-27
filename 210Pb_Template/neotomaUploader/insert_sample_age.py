import logging
from .pull_params import pull_params

def insert_sample_age(cur, yml_dict, csv_template, uploader):
    """
    """

    sample_age_query = """
                       SELECT ts.insertsampleage(_sampleid := %(sampleid)s, 
                                                 _chronologyid := %(chronologyid)s, 
                                                 _age := %(age)s, 
                                                 _ageyounger := %(ageyounger)s, 
                                                 _ageolder := %(ageolder)s)
                       """
    
    params = []
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.ages')
    
    print(len(uploader['chronology']))
    print(len(uploader['samples']))

    return