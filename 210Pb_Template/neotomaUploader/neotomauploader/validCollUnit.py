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
