import logging
from .pull_params import pull_params

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

    if isinstance(inputs['sitename'], list): 
        if len(list(set(inputs['sitename']))) > 1:
            logging.error("There should only be one site name.")
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

    try:
        coords = inputs['geog']
        assert len(coords) == 2
        assert coords[0] >= -90 and coords[0] <= 90
        assert coords[1] >= -180 and coords[1] <= 180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG' [-90 -> 90] and [-180 -> 180].")
    inputs['ew'] = coords[0]
    inputs['ns'] = coords[1]

    cur.execute(site_query,
                inputs)
    
    siteid = cur.fetchone()[0]
    return siteid
