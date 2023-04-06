def insertDataProcessor(cur, datasetid, names):
    processor = """SELECT ts.insertdataprocessor(_datasetid := %(datasetid)s,
                                                 _contactid := %(contactid)s)"""
    cur.execute(processor, {'datasetid': datasetid, 'contactid': names})
    return None
