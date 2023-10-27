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
    inputs['uncertainty'] = [float(value) if value != 'NA' else np.nan for value in inputs['uncertainty']]

    print(inputs)
    results = []

    for i, item in enumerate(uploader['samples']):
        # Matching the different kinds of  taxons
        # Have to ask about this, why is it that there are multiple taxon in the same row

        index = i % len(inputs['age'])
        
        cur.execute(sample_age_query, {'sampleid': uploader['samples'][i],
                                       'chronologyid': uploader['chronology'],
                                       'age': inputs['age'][index],
                                       'ageyounger': inputs['age'][index]-inputs['uncertainty'][index], 
                                       'ageolder': inputs['age'][index]+inputs['uncertainty'][index]})
        
        result = cur.fetchone()[0]
        results.append(result)

    return results