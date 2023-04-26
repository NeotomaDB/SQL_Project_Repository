import itertools

def validCollUnit(cur, coords, collunits):
    """Is the collection unit valid as a new unit?

    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        coords (_list_): _A list containing the coordinates for the site. We expect only a single element, a string lat/long pair._
        collunits (_list_): _A list containing unique collection unit names._

    Returns:
        _dict_: _A dict object with properties `pass` (boolean) and `collunits` (a list of valid collection units at the site). _
    """

    response = {'pass': False,
            'message': []}

    if len(coords) == 1:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': [float(i.strip()) for i in coords.split(',')][1]}
        closeSite = """
                SELECT st.*, cu.handle,
                    ST_SetSRID(ST_Centroid(st.geog::geometry), 4326)::geography <-> ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326)::geography AS dist
                FROM   ndb.sites AS st
                INNER JOIN ndb.collectionunits AS cu ON cu.siteid = st.siteid
                WHERE ST_SetSRID(ST_Centroid(st.geog::geometry), 4326)::geography <-> ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326)::geography < 10000
                ORDER BY dist;"""
        cur.execute(closeSite, coordDict)
        closeSites = cur.fetchall()

        if len(closeSites) > 0:
            goodcols = [i[-2] for i in closeSites]
            if any([j == collunits[0] for j in goodcols]):
                response['pass'] = True
                response['message'].append('✔  A collection unit with this name already exists at the site.')
            else:
                valid = False
                response['message'].append('?  The collection unit handle does not occur within close sites:')
                sitecol = itertools.groupby([{'sitename': k[1], 'collunit': k[-2]} for k in closeSites], lambda x: x['sitename'])
                sitemsg = [{'site':key, 'collunits': [k['collunit'] for k in list(value)]} for key, value in sitecol] 
                for i in sitemsg:
                    response['message'].append(f"Site: {i['site']}; collunits: {i['collunits']}")
        else:
            valid = True
            response['message'].append('✔  There are no nearby sites, a new collection unit will be created.')
    else:
        response['pass'] = False
        response['message'].append('✗  The coordinates for this site are improperly formatted.')
    return response
