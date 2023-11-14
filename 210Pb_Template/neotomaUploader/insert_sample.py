import logging
from .pull_params import pull_params
import numpy as np
import datetime

def insert_sample(cur, yml_dict, csv_template, uploader):
    """
    insert samples
    """
    sample_query = """
                   SELECT ts.insertsample(_analysisunitid := %(analysisunitid)s,
                                          _datasetid := %(datasetid)s,
                                          _samplename := %(samplename)s,
                                          _sampledate := %(sampledate)s,
                                          _analysisdate := %(analysisdate)s,
                                          _taxonid := %(taxonid)s,
                                          _labnumber := %(labnumber)s,
                                          _prepmethod := %(prepmethod)s,
                                          _notes := %(notes)s)
                    """
    
    #lab_number = yml_dict['lab_number']
    params = ['value']          
    val_inputs = pull_params(params, yml_dict, csv_template, 'ndb.data')

    params2 = ['lab_number', 'sampledate', 'analysisdate', 'labnumber', 'prepmethod', 'notes', 'taxonname', 'samplename']       
    inputs2 = pull_params(params2, yml_dict, csv_template, 'ndb.samples')
    inputs2 = dict(map(lambda item: (item[0], None if all([i is None for i in item[1]]) else item[1]),
                      inputs2.items()))

    # There might be several loops so I might need a for loop here
    samples = []

    # Assert aunits and samples are same in length
    for j, val in enumerate(uploader['anunits']):
        get_taxonid = """SELECT * FROM ndb.taxa WHERE taxonname %% %(taxonname)s;"""
        cur.execute(get_taxonid, {'taxonname': inputs2['taxonname']})
        taxonid = cur.fetchone()
        if taxonid != None:
            taxonid = int(taxonid[0])
        else:
            taxonid = None
            
        cur.execute(sample_query, {'analysisunitid': int(uploader['anunits'][j]),
                                   'datasetid': int(uploader['datasetid']),
                                   'samplename': inputs2['samplename'],
                                   'sampledate': inputs2['sampledate'], # datetime.datetime.today().date(),
                                   'analysisdate': inputs2['analysisdate'],
                                   'taxonid': taxonid,
                                   'labnumber': inputs2['lab_number'],
                                   'prepmethod': inputs2['prepmethod'],
                                   'notes': inputs2['notes']})
        sampleid = cur.fetchone()[0]
        samples.append(sampleid)
        
    return samples