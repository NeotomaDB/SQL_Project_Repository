from .retrieve_dict import retrieve_dict
from .clean_column import clean_column
import logging
from .pull_params import pull_params

def insert_analysisunit(cur, yml_dict, csv_template, uploader):
    """_Inserting analysis units_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma 
            Paleoecology Database._
        yml_dict (_dict_): _A `dict` returned by the YAML template._
        csv_template (_dict_): _The csv file with the required data to be uploaded._
        uploader (_dict_): A `dict` object that contains critical information about the
          object uploaded so far.

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """

    add_unit = """
    SELECT ts.insertanalysisunit(_collectionunitid := %(collunitid)s,
                                 _depth := %(depth)s,
                                 _thickness := %(thickness)s,
                                  _faciesid := %(faciesid)s,
                                  _mixed := %(mixed)s,
                                  _igsn := %(igsn)s,
                                  _notes := %(notes)s)
    """
    
    params = ["analysisunitname", "depth", "thickness", "faciesid", "mixed", "igsn", "notes"]
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.analysisunits')
   
    anunits = []
    for i, value in enumerate(inputs['depth']):
        if inputs['mixed'][i] == None:
            mixed_input = False
        else:
            mixed_input = inputs['mixed'][i]
        cur.execute(add_unit, {'collunitid': uploader['collunitid'],
                                'depth': inputs['depth'][i],
                                'thickness': inputs['thickness'][i],
                                'faciesid': inputs['faciesid'][i],
                                'mixed': mixed_input,
                                'igsn': inputs['igsn'][i],
                                'notes': inputs['notes'][i]})
        anunits.append(cur.fetchone()[0])
    return anunits
