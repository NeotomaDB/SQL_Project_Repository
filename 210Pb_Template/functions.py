import csv




def insertAnalysisUnit(cur, collunitid, dthick):
    addUnit = """
    SELECT ts.insertanalysisunit(_collectionunitid := %(collunitid)s, _mixed := FALSE, _depth := %(depth)s, _thickness := %(thickness)s)
    """
    anunits = []
    for i in dthick:
        cur.execute(addUnit, {'collunitid': collunitid, 'depth': i['depth'], 'thickness': i['thickness']})
        anunits.append(cur.fetchone()[0])   
    return anunits


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


def assocGeopol(cur, siteid):
    isAdded = """SELECT * FROM ap.sitegadm WHERE siteid =  %(siteid)s"""
    cur.execute(isAdded, {'siteid': siteid})
    result = cur.fetchone()[1]
    if result is None:
        assignGeoPol = """
            INSERT INTO ap.sitegadm(siteid, fid)
            (SELECT st.siteid, ga.fid
            FROM ndb.sites AS st
            JOIN ap.gadm_410 AS ga ON ST_Covers(ga.geog, st.geog)
            WHERE st.siteid = %(siteid)s);"""
        cur.execute(assignGeoPol, {'siteid': siteid})
        result = cur.fetchone()[1]
    return result


def insertChronology(cur, collunitid, agetype, agemodel, ages,
                     contactname, default = True,
                     chronologyname = 'Default 210Pb',
                     dateprepared = datetime.datetime.today().date()):
    def cleanage(x):
        try:
            y = float(x)
        except ValueError:
            y = None
        return y
        
    cleanage = list(map(lambda x: cleanage(x), ages))
    minage = min([i for i in cleanage if i is not None])
    maxage = max([i for i in cleanage if i is not None])

    addChron = """SELECT ts.insertchronology(_collectionunitid := %(collunitid)s,
        _agetypeid := %(agetype)s,
        _contactid := %(contactid)s,
        _isdefault := TRUE,
        _chronologyname := %(chronologyname)s,
        _dateprepared := %(dateprepared)s,
        _agemodel := %(agemodel)s,
        _ageboundyounger := %(maxage)s,
        _ageboundolder := %(minage)s)"""
    getCont = """SELECT contactid FROM ndb.contacts WHERE %(contactname)s %% contactname;"""    
    cur.execute(getCont, {'contactname': contactname[0]})
    contactid = cur.fetchone()[0]
    if agetype == 'cal yr BP':
        agetypeid = 2
    elif agetype == 'CE/BCE':
        agetypeid = 1
    else:
        logging.error("The provided age type is incorrect..")
    cur.execute(addChron, {'collunitid':collunitid, 'contactid': contactid,
                           'chronologyname': chronologyname,
                           'agetype': agetypeid,
                           'dateprepared': dateprepared, 'agemodel': agemodel,
                           'maxage': int(maxage), 'minage': int(minage)})
    chronid = cur.fetchone()[0]
    return chronid


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