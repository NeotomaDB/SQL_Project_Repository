from .retrieve_dict import retrieve_dict
from .clean_column import clean_column

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
                                 _mixed := FALSE,
                                 _depth := %(depth)s,
                                 _thickness := %(thickness)s,
                                  _faciesid := %(faciesid)s,
                                  _mixed := %(mixed)s,
                                  _igsn := %(igsn)s,
                                  _notes := %(notes)s)
    """

    add_unit_inputs = {}
    params = ["analysisunitname", "depth", "thickness", "faciesid", "mixed", "igsn", "notes"]
    for i in params:
        value = retrieve_dict(yml_dict, 'ndb.analysisunits.' + i)
        clean_value = [clean_column(value[j].get('column'), csv_template, clean = not value[j].get('repeat')) for j in range(len(value))]
        add_unit_inputs[i] = clean_value

    anunits = []
    for i, value in enumerate(add_unit_inputs['depth'][0]):
        cur.execute(add_unit, {'collunitid': uploader['collunitid'],
                               'depth': add_unit_inputs['depth'][0][i],
                               'thickness': add_unit_inputs['thickness'][0][i],
                               'faciesid': add_unit_inputs['thickness'][0][i],
                               'mixed': add_unit_inputs['mixed'][0][i],
                               'igsn': add_unit_inputs['igsn'][0][i],
                               'notes': add_unit_inputs['notes'][0][i]})
        anunits.append(cur.fetchone()[0])
    return anunits
