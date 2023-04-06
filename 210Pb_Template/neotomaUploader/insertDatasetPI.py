def insertDatasetPI(cur, datasetid, datasetpis):
    result = []
    getCont = """SELECT * FROM ndb.contacts WHERE contactname %% %(name)s;"""
    contids = []
    baseid = 1
    for i in datasetpis:
        cur.execute(getCont, {'name': i})
        contids.append({'name': i, 'id': cur.fetchone()[0], 'order': baseid})
        baseid = baseid + 1
    for i in contids:
        inserter = """SELECT ts.insertdatasetpi(_datasetid := %(datasetid)s, _contactid := %(contid)s);"""
        cur.execute(inserter, {'datasetid': datasetid, 'contid': contids})
        result.append(cur.fetchone()[0])
    return result
