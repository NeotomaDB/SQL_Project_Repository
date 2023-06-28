def insertSamples(cur, datasetid, annunitss):
    sampleinsert = """SELECT ts.insertsample(_analysisunitid := %(annuid)s,
                                            _datasetid := %(datasetid)s,
                                            _sampledate := %(sampdate)s,
                                            _analysisdate := %(anndate)s,
                                            _taxonid := %(taxonid)s)"""
                                            