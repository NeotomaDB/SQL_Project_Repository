def insertDataset (cur, collunitid, datasetname):
    insertString = """SELECT ts.insertdataset(
            __collectionunitid:= %(collunitid)s,
            _datasettypeid := ,
            _datasetname := %(datasetname)s);"""
    cur.execute(insertString, {'collunitid': collunitid,
                               'datasetname': datasetname})
    datasetid = cur.fetchone()[0]
    return datasetid
