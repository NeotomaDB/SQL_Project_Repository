def validCollUnit(cur, coords, collunits):
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
                    'long': [float(i.strip()) for i in coords.split(',')][1]}
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
        elif len(aa) == 1:
            valid = True
            sitelist = [{'id': str(aa[0][0]), 'name': aa[0][1], 'coordlo': str(aa[0][2]), 'coordla': str(aa[0][3]), 'distance (m)': round(aa[0][13], 0)}]
        else:
            valid = True
            sitelist = [{'id': None, 'name': None, 'coordlo': None, 'coordla': None, 'distance (m)': None}]
    else:
        valid = False
    return {'pass': valid, 'sitelist': sitelist}
