import datetime
import logging
import csv

def read_csv(filename):
    with open(filename) as f:
        file_data=csv.reader(f)
        headers=next(file_data)
        return [dict(zip(headers,i)) for i in file_data]


def validunits (template, unitcols, units) :
    invalid = []
    for i in unitcols.keys():
        for j in unitcols[i]:
            values = list(set(map(lambda x: x[j], template)))
            values = list(filter(lambda x: x != '', values))
            valid = all([k in units[i] for k in values])
            if valid == False:
                invalid.append(j)
    return invalid


def newSite(cur, coords):
    # Need to evaluate whether it's a new site, or not.
    sitelist = []
    if len(coords) == 1:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': -[float(i.strip()) for i in coords.split(',')][1]}
        closeSite = """
            SELECT st.*,
                ST_Centroid(st.geog) <-> ST_Point(%(long)s, %(lat)s, 4326) AS dist
            FROM   ndb.sites AS st
            WHERE ST_Centroid(st.geog) <-> ST_Point(%(long)s, %(lat)s, 4326) < 10000
            ORDER BY dist;"""
        cur.execute(closeSite, coordDict)
        aa = cur.fetchall()
        if len(aa) > 1:
            for i in aa:
                site = {'id': str(i[0]), 'name': i[1], 'coordlo': str(i[2]), 'coordla': str(i[3]), 'distance (m)': round(i[13], 0)}
                sitelist.append(site)
            valid = False
        else:
            valid = True
            sitelist = [{'id': str(aa[0]), 'name': aa[1], 'coordlo': str(aa[2]), 'coordla': str(aa[3]), 'distance (m)': round(aa[13], 0)}]
    else:
        valid = False
    return {'pass': valid, 'sitelist': sitelist}

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
                     name, default = True,
                     chronologyname = 'Default 210Pb',
                     dateprepared = datetime.datetime.now.date()):
    def cleanage(x):
        try:
            y = float(x)
        except ValueError:
            y = None
        return y
        
    cleanage = list(map(lambda x: cleanage(x), ages))
    
    cur = conn.cursor()
    addChron = """SELECT ts.insertchronology(_collectionunitid := %(collunitid)s,
        _agetypeid := %(agetype)s,
        _contactid := %(contactid)s,
        _isdefault := TRUE,
        _chronologyname := %(chronologyname)s,
        _dateprepared := %(dateprepared)s,
        _agemodel := %(agemodel)s,
        _ageboundyounger := %(ageyounger)s,
        _ageboundolder := %(ageolder)s)"""
    getCont = """SELECT * FROM ndb.contacts WHERE contactname %% %(name)s;"""    
    cur.execute(getCont, {'name': name})
    contactid = cur.fetchone()[0]
    if agetype == 'cal yr BP':
        agetypeid = 2
    elif agetype == 'CE/BCE':
        agetypeid = 1
    else:
        logging.error("The provided age type is incorrect..")
    cur.execute(addChron, {'collunitid':collunitid, 'contactid': contactid, 'chronologyname': chronologyname,
                           'dateprepared': dateprepared, 'agemodel': agemodel})
    
        
        

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


def validCollUnit(cur, coords, collunits):
    valid = False
    if len(coords) == 1:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': -[float(i.strip()) for i in coords.split(',')][1]}
        closeSite = """
            SELECT st.siteid, st.sitename, cu.handle,
                ST_Centroid(st.geog) <-> ST_Point(%(long)s, %(lat)s, 4326) AS dist
            FROM   ndb.sites AS st
            INNER JOIN ndb.collectionunits AS cu ON cu.siteid = st.siteid
            WHERE ST_Centroid(st.geog) <-> ST_Point(%(long)s, %(lat)s, 4326) < 1000;"""
        cur.execute(closeSite, coordDict)
        aa = cur.fetchall()
        if len(aa) > 0:
            goodcols = [i[1] for i in aa]
            if any([j == collunits[0] for j in goodcols]):
                valid = True
            else:
                valid = False
                goodcols = collunits[0]
    return {'pass': valid, 'collunits': goodcols}


def validAgent(cur, name):
    nameresults = []
    if len(name) == 1:
        nameQuery = """
            SELECT ct.contactname
            FROM ndb.contacts AS ct
            WHERE %(name)s %% ct.contactname"""
        cur.execute(nameQuery, {'name': name[0]})
        nameresults = cur.fetchall()
        if any([i[0] == name for i in nameresults]):
            result = {'pass': True, 'name': nameresults}
        else:
            result = {'pass': False, 'name': [i[0] for i in nameresults]}
    else:
        result = {'pass': False, 'name': None}
    return result


def validGeoPol(cur, geopolitical, coords):
    nameresults = []
    location = []
    if len(geopolitical) == 1:
        geopolQuery = """
            SELECT ga.fid, ga.compoundname, ts_rank(ga.ts_compoundname, plainto_tsquery('english', %(loc)s), 1) AS rank
            FROM ap.gadm_410 AS ga
            WHERE ts_rank(ga.ts_compoundname, plainto_tsquery('english', %(loc)s), 1) > 1e-3
            ORDER BY ts_rank(ga.ts_compoundname, plainto_tsquery('english', %(loc)s)) DESC;"""
        cur.execute(geopolQuery, {'loc': geopolitical[0]})
        nameresults = cur.fetchall()
    if len(coords) == 1:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': -[float(i.strip()) for i in coords.split(',')][1]}
        ingadm = """
            SELECT ga.fid, ga.compoundname
            FROM   ap.gadm_410 AS ga
            WHERE ST_Intersects(ga.geog, ST_Point(%(long)s, %(lat)s, 4326));"""
        cur.execute(ingadm, coordDict)
        location = cur.fetchall()
    if len(location) == 1 and len(nameresults) > 0:
        testlocation = any([location[0][1] == i[1] for i in nameresults])
    else:
        testlocation = False
    if testlocation is True:
        result = {'pass': True, 'fid': location[0][0], 'placename': location[0][1]}
    else:
        result = {'pass': False, 'fid': location[0][0], 'placename': location[0][1]}
    return result


def cleanCol(column, template, clean = True):
    if clean:
        setlist = list(set(map(lambda x: x[column], template)))
    else:
        setlist = list(map(lambda x: x[column], template))
    return setlist
