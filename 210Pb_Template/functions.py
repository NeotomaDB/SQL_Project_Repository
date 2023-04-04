

def insertDataset (cur, collunitid, datasetname):
    insertString = """SELECT ts.insertdataset(
            __collectionunitid:= %(collunitid)s,
            _datasettypeid := ,
            _datasetname := %(datasetname)s);"""
    cur.execute(insertString, {'collunitid': collunitid,
                               'datasetname': datasetname})
    datasetid = cur.fetchone()[0]
    return datasetid

def insertDatasetPI(cur, datasetid, piname):
    
    insertPI = """SELECT ts.insertdatasetpi(_datasetid := %(datasetid)s, 
        _contactid := %()s,
        _piorder := %(piorder)s)"""
    for i in range(len(piname)):
        cur.execute(insertPI, {'datasetid': datasetid,
                               'contactid': contactid[i],
                               'piorder': i})
    return None

def insertDataProcessor(cur, datasetid, names):
    processor = """SELECT ts.insertdataprocessor(_datasetid := %(datasetid)s,
                                                 _contactid := %(contactid)s)"""
    cur.execute(processor, {'datasetid': datasetid, 'contactid': names})
    return None


def insertSamples(cur, datasetid, annunitss):
    sampleinsert = """SELECT ts.insertsample(_analysisunitid := %(annuid)s,
                                            _datasetid := %(datasetid)s,
                                            _sampledate := %(sampdate)s,
                                            _analysisdate := %(anndate)s,
                                            _taxonid := %(taxonid)s)"""

                                            
def insertSampleAges(cur):
    sampleageinsert = """
    """

#def insertSampleAnalyst(cur):

#def insertData(cur):