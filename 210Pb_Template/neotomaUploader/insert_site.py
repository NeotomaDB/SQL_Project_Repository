import logging
from .pull_params import pull_params
from .retrieve_dict import retrieve_dict

def insert_site(cur, yml_dict, csv_template):
    """_Insert a site to Neotoma_

    def insertSite(cur, yml_dict, csv_template)

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma 
            Paleoecology Database._
        yml_dict (_dict_): _A `dict` returned by the YAML template._
        csv_template (_dict_): _The csv file with the required data to be uploaded._

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """
    site_query = """
        SELECT ts.insertsite(_sitename := %(sitename)s, 
                             _altitude := %(altitude)s,
                             _area := %(area)s,
                             _descript := %(description)s,
                             _notes := %(notes)s,
                             _east := %(ew)s,
                             _north := %(ns)s,
                             _west := %(ew)s,
                             _south := %(ns)s)
                """
    try:
        # Here we're just checking to make sure that we do have a site coordinate
        # and geometry.
        assert all(element in [d.get('neotoma') for d in yml_dict.get('metadata')]
                   for element in ['ndb.sites.sitename', 'ndb.sites.geog'])
    except AssertionError:
        logging.error("The template must contain a sitename and coordinates.", exc_info=True)
    params = ["sitename", "altitude", "area", "sitedescription", "notes", "geog"]
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.sites')
    inputs = dict(map(lambda item: (item[0], None if all([i is None for i in item[1]]) else item[1]),
                      inputs.items()))
    
    if len(inputs['sitename']) == 1 and isinstance(inputs['sitename'], list):
        inputs['sitename'] = inputs['sitename'][0]
    if inputs['altitude'] is not None:
        inputs['altitude'] = inputs['altitude'][0]
    if inputs['area'] is not None:
        inputs['area'] = inputs['area'][0]
    if inputs['sitedescription'] is not None:
        inputs['description'] = inputs['sitedescription'][0]
    else:
        inputs['description'] = None
    if inputs['notes'] is not None:
        inputs['notes'] = inputs['notes'][0]
    if len(inputs['geog']) == 1 and isinstance(inputs['geog'], list):
        geog = retrieve_dict(yml_dict, 'ndb.sites.geog')[0]
        inputs['geog'] = inputs['geog'][0]
        if geog['type'] == 'coordinates (latlong)':
            inputs['ew'] = inputs['geog'][0]
            inputs['ns'] = inputs['geog'][1]

    cur.execute(site_query,
                inputs)
    siteid = cur.fetchone()[0]
    return siteid
