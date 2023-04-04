def insertAnalysisUnit(cur, collunitid, dthick):
    addUnit = """
    SELECT ts.insertanalysisunit(_collectionunitid := %(collunitid)s, _mixed := FALSE, _depth := %(depth)s, _thickness := %(thickness)s)
    """
    anunits = []
    for i in dthick:
        cur.execute(addUnit, {'collunitid': collunitid, 'depth': i['depth'], 'thickness': i['thickness']})
        anunits.append(cur.fetchone()[0])   
    return anunits
