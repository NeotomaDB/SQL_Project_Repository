def validGeoPol(cur, geopolitical, coords):
    """_Is the listed geopolitical unit valid?_

    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        geopolitical (_list_): _The set of valid geopolitical unit names assigned to the site._
        coords (_list_): _A list containing the coordinates for the site. We expect only a single element, a string lat/long pair._

    Returns:
        _dict_: _A dict with properties pass, fid (the unique geoplacename identifier) and the valid `placename`._
    """
    
    response = {'pass': False,
                'locations': [],
                'message': []}
    
    if len(coords) != 1:
        # Finish the function:
        response['message'].append('✗  Site coordinates are improperly formatted.')
        return response
    else:
        coords = coords[0]
        coordDict = {'lat': [float(i.strip()) for i in coords.split(',')][0],
                    'long': [float(i.strip()) for i in coords.split(',')][1]}
        ingadm = """
            SELECT ga.fid, ga.compoundname
            FROM   ap.gadm_410 AS ga
            WHERE ST_Intersects(ST_SetSRID(ga.shape, 4326), ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326));"""
        cur.execute(ingadm, coordDict)
        location = cur.fetchall()
    if len(geopolitical) == 1:
        geopolQuery = """
            SELECT ga.fid, ga.compoundname, ts_rank(ga.ts_compoundname, plainto_tsquery('english', %(loc)s), 1) AS rank
            FROM ap.gadm_410 AS ga
            WHERE ts_rank(ga.ts_compoundname, plainto_tsquery('english', %(loc)s), 1) > 1e-3
            ORDER BY ts_rank(ga.ts_compoundname, plainto_tsquery('english', %(loc)s)) DESC;"""
        cur.execute(geopolQuery, {'loc': geopolitical[0]})
        nameresults = cur.fetchall()
    else:
        nameresults = []
    if len(location) == 1 and len(nameresults) > 0:
        testlocation = any([location[0][1] == i[1] for i in nameresults])
    else:
        testlocation = False

    if testlocation is True:
        # The name of the geopolitical unit matches the user supplied name:
        response['pass'] = True
        response['locations'] = location[0][1]
        response['message'].append("✔  The provided geopolitical unit matches an existing geopolitical unit within Neotoma.")
    elif testlocation is False and len(location) > 0:
        response['pass'] = False
        response['locations'] = location[0][1]
        response['message'].append("✗  The provided geopolitical unit does not match an existing geopolitical unit within Neotoma.")
        response['message'].append(f"  * Best match: {response['locations']}.")
    
    return response
