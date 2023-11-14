import logging
from .pull_params import pull_params

def insert_data(cur, yml_dict, csv_template, uploader):
    data_query = """
                 SELECT ts.insertdata(_sampleid := %(sampleid)s,
                                      _variableid := %(variableid)s,
                                      _value := %(value)s)
                 """
    params = ['value']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.data')
    data_points = []
    for i, val_dict in enumerate(inputs):
        val_dict['value'] = [None if item == 'NA' else item for item in val_dict['value']]
        val_dict['variableelementid'] = None # placeholder
        val_dict['variablecontextid'] = None # placeholder
        
        # Getting TaxonID
        get_taxonid = """SELECT * FROM ndb.taxa WHERE taxonname %% %(taxonname)s;"""
        cur.execute(get_taxonid, {'taxonname': inputs[i]['taxonname']})
        taxonid = cur.fetchone()
        if taxonid != None:
            taxonid = int(taxonid[0])
        else:
            #print(inputs[i]['taxonname'])
            taxonid = 5 #placeholder
            
        for j, val in enumerate(val_dict['unitcolumn']):
            # Get UnitsID
            get_unitsid = """SELECT * FROM ndb.variableunits WHERE variableunits %% %(units)s;"""
            cur.execute(get_unitsid, {'units': val_dict['unitcolumn'][j]})
            unitsid = cur.fetchone()[0] # This is just getting the varunitsid

            get_varid = """SELECT * FROM ndb.variables 
                           WHERE variableunitsid = %(unitsid)s 
                           AND taxonid = %(taxonid)s
                           AND variableelementid = %(variableelementid)s
                           AND variablecontextid = %(variablecontextid)s
                           """
            cur.execute(get_varid, {'unitsid':unitsid, 'taxonid': taxonid, 'variableelementid': val_dict['variableelementid'], 'variablecontextid': val_dict['variablecontextid']})
            varid = cur.fetchone()
            if varid != None:
                varid = int(varid[0])
            else:
                var_query = """SELECT ts.insertvariable(_taxonid := %(taxonid)s,
                                            _variableelementid := %(variableelementid)s,
                                            _variableunitsid := %(variableunitsid)s,
                                            _variablecontextid := %(variablecontextid)s)"""
                cur.execute(var_query, {'taxonid': taxonid,
                                        'variableelementid': None,
                                        'variableunitsid': unitsid,
                                        'variablecontextid': None}) # inputs[i]['variablecontextid']})
                varid = cur.fetchone()[0]
            cur.execute(data_query, {'sampleid': int(uploader['samples'][i]),
                                    'variableid': int(varid),
                                    'value': val_dict['value'][i]})
        
            result = cur.fetchone()[0]
            data_points.append(result)

    return data_points