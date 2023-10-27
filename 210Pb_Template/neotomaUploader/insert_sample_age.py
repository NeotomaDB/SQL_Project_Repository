import logging
from .pull_params import pull_params
import numpy as np

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
    
    params = ['age']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.sampleages')

    inputs['age'] = [float(value) if value != 'NA' else np.nan for value in inputs['age']]

    print(inputs)
    results = []
    for i in range(len(uploader['samples'])):
        cur.execute(sample_age_query, {'sampleid': uploader['samples'][i],
                                       'chronologyid': uploader['chronologyid'],
                                       'age': inputs['age'],
                                       'ageyounger': inputs['ageyounger'],
                                       'ageolder': inputs['ageolder']})
        result = cur.fetchone()[0]
        results.append(result)

    return results