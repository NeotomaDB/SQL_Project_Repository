import logging
from .pull_params import pull_params
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

    params2 = ['lab_number', 'sampledate', 'analysisdate', 'labnumber', 'prepmethod', 'notes']       
    inputs2 = pull_params(params2, yml_dict, csv_template, 'ndb.data')
    inputs2 = dict(map(lambda item: (item[0], None if all([i is None for i in item[1]]) else item[1]),
                      inputs2.items()))

    # There might be several loops so I might need a for loop here
    samples = []

    for j, val in enumerate(val_inputs):
        for i, value in enumerate(uploader['anunits']):
            get_taxonid = """SELECT * FROM ndb.taxa WHERE taxonname %% %(taxonname)s;"""
            cur.execute(get_taxonid, {'taxonname': val_inputs[j]['taxonname']})
            taxonid = cur.fetchone()
            
            if taxonid is None:
                # Inserts taxonid in taxonname if it didn't exist ???
                # How does this behave with Tilia
                assigntaxonID = """
                SELECT ts.inserttaxon(_code := %(code)s,
                                      _name := %(name)s,
                                      _extinct := %(extinct)s,
                                      _groupid := %(groupid)s,
                                      _author := %(author)s,
                                      _valid := %(valid)s,
                                      _higherid := %(higherid)s,
                                      _pubid := %(pubid)s,
                                      _validatorid := %(validatorid)s,
                                      _validatedate := %(validatedate)s,
                                      _notes := %(notes)s)
                    """     
                #cur.execute(assigntaxonID, {code: code,
                                    #        name: name,
                                    #        extinct: extinct,
                                    #        groupid: groupid,
                                    #        author: author,
                                    #        valid: valid,
                                    #        higherid: higherid,
                                    #        pubid: pubid,
                                    #        validatorid: validatorid,
                                    #        validatedate: validatedate,
                                    #        notes: notes})
                # taxonid = cur.fetchone()[0]
                taxonid = 5
            else:
                taxonid = taxonid[0]
            
            cur.execute(sample_query, {'analysisunitid': int(uploader['anunits'][i]),
                                       'datasetid': int(uploader['datasetid']),
                                       'samplename': val_inputs[j]['taxonname'],
                                       'sampledate': inputs2['sampledate'], # datetime.datetime.today().date(),
                                       'analysisdate': inputs2['analysisdate'],
                                       #'taxonid': int(val_inputs[i]['taxonid']),
                                       'taxonid': int(taxonid),
                                       'labnumber': inputs2['lab_number'],
                                       'prepmethod': inputs2['prepmethod'],
                                       'notes': inputs2['notes']})
            sampleid = cur.fetchone()[0]
            samples.append(sampleid)
        
    return samples