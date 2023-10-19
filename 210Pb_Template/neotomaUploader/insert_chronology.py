import datetime
import logging
import datetime
import numpy as np
from .pull_params import pull_params

def insert_chronology(cur, yml_dict, csv_template, uploader):
    addChron = """
    SELECT ts.insertchronology(_collectionunitid := %(collunitid)s,
                               _agetypeid := %(agetype)s,
                               _contactid := %(contactid)s,
                               _isdefault := TRUE,
                               _chronologyname := %(chronologyname)s,
                               _dateprepared := %(dateprepared)s,
                               _agemodel := %(agemodel)s,
                               _ageboundyounger := %(maxage)s,
                               _ageboundolder := %(minage)s)
                """
    
    get_cont = """SELECT contactid FROM ndb.contacts WHERE %(contactname)s = contactname;"""    
    
    params = ["contactid", "agemodel", "notes"]
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.chronologies')

    params2 = ['age']
    inputs_age = pull_params(params2, yml_dict, csv_template, 'ndb.sampleages')

    inputs_age['age'] = [float(value) if value != 'NA' else np.nan for value in inputs_age['age']]
    agetype = list(set(inputs_age['unitcolumn']))
    agetype = agetype[0]

    cur.execute(get_cont, {'contactname': inputs['contactid'][0]})
    contactid = cur.fetchone()[0]

    if agetype == 'cal yr BP':
        agetypeid = 2
    elif agetype == 'CE/BCE':
        agetypeid = 1
    else:
        logging.error("The provided age type is incorrect..")

    cur.execute(addChron, {'collunitid': int(uploader['collunitid']), 
                           'contactid': contactid,
                           'chronologyname': 'Default 210Pb',  # This is a default but might be better to specify in template
                           'agetype': agetypeid, # Comming from column X210Pb.Date.Units which should be linked to params3
                           'dateprepared': datetime.datetime.today().date(),  # Default but should be coming from template s
                           'agemodel': inputs['agemodel'][0],
                           'maxage': int(max(inputs_age['age'])), 
                           'minage': int(min(inputs_age['age']))})
    chronid = cur.fetchone()[0]
    
    return chronid
