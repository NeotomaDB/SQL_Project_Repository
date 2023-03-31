import datetime

def validCollUnit(cur, coords, collunits):
    """Is the collection unit valid as a new unit?

    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        coords (_list_): _A list containing the coordinates for the site. We expect only a single element, a string lat/long pair._
        collunits (_list_): _A list containing unique collection unit names._

    Returns:
        _dict_: _A dict object with properties `pass` (boolean) and `collunits` (a list of valid collection units at the site). _
    """    
    valid = False
    if len(coords) == 1:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': [float(i.strip()) for i in coords.split(',')][1]}
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
        else:
            valid = True
            goodcols = []  
    else:
        valid = False
        goodcols = []
    return {'pass': valid, 'collunits': goodcols}


def validAgent(cur, name):
    """_Is the contact name valid and in the database?_

    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        name (_list_): _A list containing valid agent/contact names._

    Returns:
        _dict_: _A dict with two parameters, `pass` (boolean) and `name`, a list of valid names with approximate matches._
    """
    nameresults = []
    if len(name) == 1:
        nameQuery = """
            SELECT ct.contactname
            FROM ndb.contacts AS ct
            WHERE %(name)s %% ct.contactname"""
        cur.execute(nameQuery, {'name': name[0]})
        nameresults = cur.fetchall()
        if any([i[0] == name[0] for i in nameresults]):
            result = {'pass': True, 'name': nameresults}
        else:
            result = {'pass': False, 'name': [i[0] for i in nameresults]}
    else:
        result = {'pass': False, 'name': None}
    return result


def validGeoPol(cur, geopolitical, coords):
    """_Is the listed geopolitical unit valid?_

    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        geopolitical (_list_): _The set of valid geopolitical unit names assigned to the site._
        coords (_list_): _A list containing the coordinates for the site. We expect only a single element, a string lat/long pair._

    Returns:
        _dict_: _A dict with properties pass, fid (the unique geoplacename identifier) and the valid `placename`._
    """
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
    if len(coords) > 0:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': [float(i.strip()) for i in coords.split(',')][1]}
        ingadm = """
            SELECT ga.fid, ga.compoundname
            FROM   ap.gadm_410 AS ga
            WHERE ST_Intersects(ga.geog, ST_Point(%(long)s, %(lat)s, 4326));"""
        cur.execute(ingadm, coordDict)
        location = cur.fetchall()
    elif len(coords) == 0:
        location = []

    if len(location) == 1 and len(nameresults) > 0:
        testlocation = any([location[0][1] == i[1] for i in nameresults])
    else:
        testlocation = False

    if testlocation is True:
        result = {'pass': True, 'fid': location[0][0], 'placename': location[0][1]}
    elif testlocation is False and len(location) > 0:
        result = {'pass': False, 'fid': location[0][0], 'placename': location[0][1]}
    else:
        result = {'pass': False, 'fid': [], 'placename': []}
    return result


def validunits (template, unitcols, units):
    """_Are the units provided valid based on defined unit names?_

    Args:
        template (_list_): _The csv file content, as a list._
        unitcols (_dict_): _The names of each set of columns listing units in the file, with a key linked to the `units` column._
        units (_dict_): _Acceptable units for each data column type._

    Returns:
        _list_: _A list of columns with invalid units._
    """    
    invalid = []
    for i in unitcols.keys():
        for j in unitcols[i]:
            values = list(set(map(lambda x: x[j], template)))
            values = list(filter(lambda x: x != '', values))
            valid = all([k in units[i] for k in values])
            if valid == False:
                invalid.append(j)
    return invalid


def validSite(cur, coords):
    """_Is the site a valid new site?_
    
    The function accepts a set of coordinates, a site name, and returns a dict with the properties:
        * `pass`: Did the operation work as expected (a site is matched and a valid siteid returned).
        * `sitelist`: A list of site dicts including {'siteid', 'sitename', 'lat', 'long', 'distance'}
    
    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        coords (_list_): _A list containing the coordinates for the site. We expect only a single element, a string lat/long pair._
        sitename (_string_): The unique site name for the record.

    Returns:
        _dict_: _A dict object with two properties, the boolean `pass` and a `sitelist` with all close sites._
    """
    # Need to evaluate whether it's a new site, or not.
    sitelist = []
    if len(coords) == 1:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': [float(i.strip()) for i in coords.split(',')][1]}
        closeSite = """
            SELECT st.*,
                ST_Centroid(st.geog) <-> ST_Point(%(long)s, %(lat)s, 4326) AS dist
            FROM   ndb.sites AS st
            WHERE ST_Centroid(st.geog) <-> ST_Point(%(long)s, %(lat)s, 4326) < 10000
            ORDER BY dist;"""
        cur.execute(closeSite, coordDict)
        aa = cur.fetchall()
        if len(aa) > 0:
            for i in aa:
                site = {'id': str(i[0]), 'name': i[1], 'coordlo': str(i[2]), 'coordla': str(i[3]), 'distance (m)': round(i[13], 0)}
                valid = False
                sitelist.append(site)
        else:
            valid = True
            sitelist = [{'id': None, 'name': None, 'coordlo': None, 'coordla': None, 'distance (m)': None}]
    else:
        valid = False
    return {'pass': valid, 'sitelist': sitelist}


def validCollDate(colldate):
    try:
        newdate = datetime.datetime.strptime(colldate[0], '%Y-%m-%d').date()
    except ValueError:
        return {'valid': False, 'date': 'Expected date format is YYYY-mm-dd'}
    return {'valid': True, 'date': newdate}


def validHorizon(depths, horizon):
    if len(horizon) == 1:
        matchingdepth = [i == horizon[0] for i in depths]
        if any(matchingdepth):
            valid = True
            hmatch = { 'index': next(i for i,v in enumerate(matchingdepth) if v) }
        else:
            valid = False
            hmatch = { 'index': -1 }
    else:
        valid = False
        hmatch = { 'index': None }
    return {'valid': valid, 'index': hmatch}
