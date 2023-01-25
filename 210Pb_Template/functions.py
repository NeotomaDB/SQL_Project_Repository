import datetime
import logging
import csv

def read_csv(filename):
    with open(filename) as f:
        file_data=csv.reader(f)
        headers=next(file_data)
        return [dict(zip(headers,i)) for i in file_data]


def insertSite(conn, sitename, coords):
    """_summary_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        sitename (_list_): _A list returned by the function cleanCol()_
        coords (_list_): _A list returned by the function cleanCol()_

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """    
    cur = conn.cursor()
    try:
        assert len(sitename) == 1
    except AssertionError:
        logging.error("Only one single site name should be returned.", exc_info=True)
    try:
        coords = list(map(lambda x: float(x), coords[0].split(',')))
        assert len(coords) == 2
        assert coords[0] >= 0 and coords[0] <= 90
        assert coords[1] >= 0 and coords[1] <= 180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG'.")
    sitename = sitename[0]       
    cur.execute("SELECT ts.insertsite(_sitename := %(sitename)s, _east := %(ew)s, _north := %(ns)s, _west := %(ew)s, _south := %(ns)s)",
                {'sitename': sitename, 'ew': coords[1], 'ns': coords[0]})
    siteid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return siteid


def insertCollUnit(conn, collunits, colldate, siteid, coords, location):
    cur = conn.cursor()
    newdate = datetime.datetime.strptime(colldate[0], '%d-%m-%Y').date()
    handle = collunits[0].upper().replace(' ', '')[0:9]
    try:
        coords = list(map(lambda x: float(x), coords[0].split(',')))
        assert len(coords) == 2
        assert coords[0] >= 0 and coords[0] <= 90
        assert coords[1] >= 0 and coords[1] <= 180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG'.")
    cur.execute("""
        SELECT ts.insertcollectionunit(
            _handle := %(handle)s,
            _collunitname := %(collname)s,
            _siteid := %(siteid)s, 
            _colltypeid := 3,
            _depenvtid := 24, 
            _colldate := %(newdate)s,
            _location := %(location)s,
            _gpslatitude := %(ns)s, _gpslongitude := %(ew)s)""",
          {'collname': collunits[0], 'newdate': newdate, 'siteid' : siteid,
           'handle': handle, 'location': location[0],
           'ns': coords[0], 'ew': coords[1]})
    collunitid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return collunitid


def insertAnalysisUnit(conn, collunitid, dthick):
    cur = conn.cursor()
    addUnit = """
    SELECT ts.insertanalysisunit(_collectionunitid := %(collunitid)s, _mixed := FALSE, _depth := %(depth)s, _thickness := %(thickness)s)
    """
    anunits = []
    for i in dthick:
        cur.execute(addUnit, {'collunitid': collunitid, 'depth': i['depth'], 'thickness': i['thickness']})
        anunits.append(cur.fetchone()[0])
    conn.commit()
    cur.close()    
    return anunits


def insertChronology(conn, collunitid, agetype, agemodel, ages,
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
    
    cur = conn.cursor()
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

def insertDatasetPI(conn, datasetid, datasetpis):
    cur = conn.cursor()
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
    conn.commit()
    cur.close()
    return result


def assocGeopol(conn, siteid):
    cur = conn.cursor()
    assignGeoPol = """
        INSERT INTO ap.sitegadm(siteid, fid)
        (SELECT st.siteid, ga.fid
        FROM ndb.sites AS st
        JOIN ap.gadm_410 AS ga ON ST_Covers(ga.geog, st.geog)
        WHERE st.siteid = %(siteid)s);"""
    cur.execute(assignGeoPol, {'siteid': siteid})
    result = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return result


def cleanCol(column, template, clean = True):
    if clean:
        setlist = list(set(map(lambda x: x[column], template)))
    else:
        setlist = list(map(lambda x: x[column], template))
    return setlist
