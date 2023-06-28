from .retrieveDict import retrieveDict
from .cleanCol import cleanCol

def insertAnalysisUnit(cur, yml_dict, csvTemplate, uploader):
    """_Inserting analysis units_

    Args:
        cur (_type_): _description_
        yml_dict (_type_): _description_
        csvTemplate (_type_): _description_
        uploader (_type_): _description_

    Returns:
        _type_: _description_
    """
    addUnit = """
    SELECT ts.insertanalysisunit(_collectionunitid := %(collunitid)s, _mixed := FALSE, _depth := %(depth)s, _thickness := %(thickness)s)
    """

    depthD = retrieveDict(yml_dict, 'ndb.analysisunits.depth')
    thickD = retrieveDict(yml_dict, 'ndb.analysisunits.thickness')

    depths = cleanCol(depthD.get('column'),
                            csvTemplate,
                            clean = not depthD.get('repeat'))

    thicks = cleanCol(thickD.get('column'),
                            csvTemplate,
                            clean = not thickD.get('repeat'))

    anunits = []
    for i, value in enumerate(depths):
        cur.execute(addUnit, {'collunitid': uploader['collunitid'],
                              'depth': value, 'thickness': thicks[i]})
        anunits.append(cur.fetchone()[0])
    return anunits
