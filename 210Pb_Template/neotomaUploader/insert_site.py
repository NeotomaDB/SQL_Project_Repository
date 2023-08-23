import logging
from .yaml_values import yaml_values

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
                             _altitude := %(altitude)d,
                             _area := %(altitude)d,
                             _description := %(description)s,
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
    cur.execute(,
                {'sitename': sitename_dict[0].get('values')[0], 'ew': coords[1], 'ns': coords[0]})
    siteid = cur.fetchone()[0]
    return siteid
