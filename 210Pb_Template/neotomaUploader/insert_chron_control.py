import logging
import numpy as np
from .pull_params import pull_params

def insert_chron_control(cur, yml_dict, csv_template, uploader):
    addcontrol = """
        SELECT ts.insertchroncontrol(_chronologyid := %(chronid)s,
            _chroncontroltypeid := 10,
            _analysisunitid := %(annuid)s,
            _depth := %(depth)s,
            _thickness := %(thickness)s,
            _agetypeid := %(agetypeid)s,
            _age := %(age)s,
            _agelimityounger := %(ageyoung)s,
            _agelimitolder := %(ageold)s,
            _notes := %(notes)s)"""
    
    params = ["depth", "thickness", 'notes',]
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.analysisunits')

    params_age = ['age']
    inputs_age = pull_params(params_age, yml_dict, csv_template, 'ndb.sampleages')

    inputs_age['age'] = [float(value) if value != 'NA' else np.nan for value in inputs_age['age']]
    inputs_age['uncertainty'] = [float(value) if value != 'NA' else np.nan for value in inputs_age['uncertainty']]
    agetype = list(set(inputs_age['unitcolumn']))
    agetype = agetype[0]
    
    assert len(uploader['anunits']) == len(inputs_age['age']) == len(inputs['thickness']), \
           "The number of analysis units, ages, and thicknesses is not the same. Please check."

    chron_control_units = list()
    for i in range(len(uploader['anunits'])):
        if inputs_age['unitcolumn'][i] == 'cal yr BP':
            agetypeid = 2
        elif inputs_age['unitcolumn'][i] == 'CE/BCE':
            agetypeid = 1
        else:
            logging.error("The provided age type is incorrect..")
        cur.execute(addcontrol, {'chronid': int(uploader['chronology']),
                                 'annuid': int(uploader['anunits'][i]),
                                 'depth': inputs['depth'][i],
                                 'thickness': inputs['thickness'][i],
                                 'agetypeid': agetypeid,
                                 'age': inputs_age['age'][i],
                                 'notes':inputs['notes'][i],
                                 'ageyoung': inputs_age['age'][i] + inputs_age['uncertainty'][i],
                                 'ageold': inputs_age['age'][i] -  inputs_age['uncertainty'][i]})
        chron_control_units.append(cur.fetchone()[0])
    return chron_control_units