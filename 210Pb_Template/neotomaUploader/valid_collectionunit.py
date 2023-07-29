import itertools
from .yaml_values import yaml_values

def valid_collectionunit(cur, yml_dict, csv_template):
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

    coords = yaml_values(yml_dict, csv_template, 'ndb.sites.geom')
    try:
        assert len(coords) == 1
    except AssertionError:
        if len(coords) > 1:
            response['message'].append('✗ There are multiple columns mapped to coordinates in your template.')
        else:
            response['message'].append('✗ There are no columns mapped to coordinates in your template.')
        return response
    sitename = yaml_values(yml_dict, csv_template, 'ndb.sites.sitename')
    try:
        assert len(sitename) == 1
    except AssertionError:
        if len(sitename) > 1:
            response['message'].append('✗ There are multiple columns mapped to sitenames in your template.')
        else:
            response['message'].append('✗ There are no columns mapped to sitenames in your template.')

    handlename = yaml_values(yml_dict, csv_template, 'ndb.collectionunits.handle')
    try:
        assert len(handlename) == 1
    except AssertionError:
        response['message'].append('✗ There can only be a single collection unit handle defined.')
    
    if len(coords) == 1:
        coord_list = [float(i) for i in coords[0].get('values')[0].split(',')]
        coord_dict = {'lat': coord_list[0],
                      'long': coord_list[1]}
        close_site = """
                SELECT st.*, cu.handle,
                    ST_SetSRID(ST_Centroid(st.geog::geometry), 4326)::geography <-> ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326)::geography AS dist
                FROM   ndb.sites AS st
                INNER JOIN ndb.collectionunits AS cu ON cu.siteid = st.siteid
                WHERE ST_SetSRID(ST_Centroid(st.geog::geometry), 4326)::geography <-> ST_SetSRID(ST_Point(%(long)s, %(lat)s), 4326)::geography < 10000
                ORDER BY dist;"""
        cur.execute(close_site, coord_dict)
        close_sites = cur.fetchall()

        if len(close_sites) > 0:
            goodcols = [i[-2] for i in close_sites]
            if any([j == handlename[0] for j in goodcols]):
                response['pass'] = True
                response['message'].append('✔  A collection unit with this name already exists at the site.')
            else:
                response['message'].append('?  The collection unit handle does not occur within close sites:')
                sitecol = itertools.groupby([{'sitename': k[1], 'collunit': k[-2]} for k in close_sites], lambda x: x['sitename'])
                sitemsg = [{'site':key, 'collunits': [k['collunit'] for k in list(value)]} for key, value in sitecol] 
                for i in sitemsg:
                    response['message'].append(f"Site: {i['site']}; collunits: {i['collunits']}")
        else:
            response['message'].append('✔  There are no nearby sites, a new collection unit will be created.')
    else:
        response['pass'] = False
        response['message'].append('✗  The coordinates for this site are improperly formatted.')
    return response