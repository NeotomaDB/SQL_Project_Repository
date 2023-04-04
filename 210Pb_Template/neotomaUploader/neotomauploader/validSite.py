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
