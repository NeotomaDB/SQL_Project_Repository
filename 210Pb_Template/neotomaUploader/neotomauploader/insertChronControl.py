import logging

def insertChronControl(cur, chronid, annunits, dthick,
                       agetype):
    for i in range(len(dthick)):
        dthick[i]['annunit'] = annunits[i]

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
    for i in dthick:
        if agetype == 'cal yr BP':
            agetypeid = 2
        elif agetype == 'CE/BCE':
            agetypeid = 1
        else:
            logging.error("The provided age type is incorrect..")
        cur.execute(addcontrol, {'chronid': chronid,
                                 'annuid': i['annunit'],
                                 'depth': i['depth'],
                                 'thickness': i['thick'],
                                 'agetypeid': agetypeid,
                                 'age': i['age'],
                                 'ageyoung': i['age'] + i['error'],
                                 'ageold': i['age'] - i['error']})
    return None

