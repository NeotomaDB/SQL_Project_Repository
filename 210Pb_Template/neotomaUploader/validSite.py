from .retrieveColumn import retrieveColumn
import pandas as pd
#def validSite(cur, coords, hemisphere, sitename):
def validSite(cur, yml_dict, df, sites_str):
    """_Is the site a valid new site?_
    The function accepts a set of coordinates, a site name, and the appropriate hemisphere and 
    returns a dict with the properties:
        * `pass`: Did the operation work as expected (a site is matched and a valid siteid returned).
        * `sitelist`: A list of site dicts including {'siteid', 'sitename', 'lat', 'long', 'distance'}
        * `hemisphere`: Does the site exist within the expected hemispheres?
        * `matched`: Given a set of "close" sites, does one of them also have the right name? This dict includes two
        properties
            * `namematch`: does one of the close sites have the same name as the target site?
            * `distmatch`: is one site coincident with the current site coordinates?
    Args:
        cur (_psycopg2.extensions.connection_): _A connection to a valid Neotoma database (either local or remote)_
        coords (_list_): _A list containing the coordinates for the site. We expect only a single element, a string lat/long pair._
        hemisphere (_list_): _A single character string, or set of strings indicating acceptable global quadrants for the site (NW, NE, SW, SE)._
        sitename (_string_): The unique site name for the record.
    Returns:
        _dict_: _A dict object with two properties, the boolean `pass` and a `sitelist` with all close sites._
    """
    response = {'pass': False,
                'hemisphere': False,
                'sitelist': [],
                'matched': {'namematch': False, 'distmatch': False},
                'message': []}
    
    ## Retrieve the fields needed from the yml.
    coords = retrieveColumn(yml_dict, 'ndb.sites.geom')
    coords = coords['column']
    coords = list(df[coords].unique())

    sitename = retrieveColumn(yml_dict, sites_str)
    sitename = sitename['column']
    sitename = list(df[sitename].unique())
    
    # Need to evaluate whether it's a new site, or not.
    sitelist = []
    if len(coords) != 1:
        # Finish the function:
        response['message'].append('✗ Site coordinates are improperly formatted.')
        return response
    coo = coords[0]
    coordDict = {'lat': [float(i.strip()) for i in coo.split(',')][0],
                'long': [float(i.strip()) for i in coo.split(',')][1]}
    
    # Get the allowed hemispheres for the record.
    hemis = ""
    if coordDict['lat'] >= 0:
        hemis+="N"
    else:
        hemis+="S"
    if coordDict['long'] >= 0:
        hemis+="E"
    else:
        hemis+="W"
    response['message'].append(f'? This set is expected to be in the {hemis} hemisphere.')  
    
    closeSite = """
        SELECT st.*,
            ST_SetSRID(ST_Centroid(st.geog::geometry), 4326)::geography <-> ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326)::geography AS dist
        FROM   ndb.sites AS st
        WHERE ST_SetSRID(ST_Centroid(st.geog::geometry), 4326)::geography <-> ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326)::geography < 10000
        ORDER BY dist;"""
    cur.execute(closeSite, coordDict)
    closeSites = cur.fetchall()
    if len(closeSites) > 0:
        # There are sites within 10km get the siteid, name, coordinates and distance.
        response['valid'] = False
        response['message'].append('?  One or more sites exist close to the requested site.')
        for i in closeSites:
            site = {'id': str(i[0]), 'name': i[1], 'coordlo': str(i[2]), 'coordla': str(i[3]), 'distance (m)': round(i[13], 0)}
            response['sitelist'].append(site)
        response['matched']['namematch'] = any([x['name'] == sitename for x in response['sitelist']])
        if response['matched']['namematch']:
            response['matched']['distmatch'] = response['sitelist'][[x['name'] == sitename for x in response['sitelist']].index(True)]['distance (m)'] == 0
        if response['matched']['namematch'] and response['matched']['distmatch']:
            response['valid'] = True
            response['message'].append('✔  Valid site: Site currently exists at the reported location and the name is matched.')
        elif response['matched']['namematch']:
            response['valid'] = False
            response['message'].append('?  Site name matches, but locations differ.')
        elif response['matched']['distmatch']:
            response['valid'] = False
            response['message'].append('?  Location matches, but site names differ.')
        if response['valid'] == False:
            for i in response['sitelist']:
                response['message'].append(f"  * siteid: {i['id']};  sitename: {i['name']:<25}; distance (m): {i['distance (m)']:<7} coords: [{i['coordla']}, {i['coordlo']}]")
    else:
        valid = True
        sitelist = [{'id': None, 'name': None, 'coordlo': None, 'coordla': None, 'distance (m)': None}]
        response['matched'] = {'namematch': False, 'distmatch': False}
        response['message'].append('✔  There are no sites close to the proposed site.')
    return response