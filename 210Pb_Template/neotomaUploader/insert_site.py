import logging
from .yaml_values import yaml_values

def insert_site(cur, yml_dict, csv_template):
    """_Insert a site to Neotoma_

    def insertSite(cur, yml_dict, csv_template)

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        sitename (_list_): _A list returned by the function cleanCol()_
        coords (_list_): _A list returned by the function cleanCol()_

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """
    try:
        assert all(element in [d.get('neotoma') for d in yml_dict.get('metadata')]
                   for element in ['ndb.sites.sitename', 'ndb.sites.geom'])
    except AssertionError:
        logging.error("The template must contain a sitename and coordinates.", exc_info=True)
    try:
        coord_dict = yaml_values(yml_dict, csv_template, 'ndb.sites.geom')
        coords = [float(i) for i in coord_dict[0].get('values')[0].split(',')]
        assert len(coords) == 2
        assert coords[0] >= 0 and coords[0] <= 90
        assert coords[1] <= 0 and coords[1] >= -180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG'.")
    try:
        sitenameDict = yaml_values(yml_dict, csv_template, 'ndb.sites.sitename')
        assert len(sitenameDict) == 1
        assert isinstance(sitenameDict[0].get('values')[0], str)
    except AssertionError:
        logging.error("A single sitename value must be provided. Check your yaml template to be sure.")

    cur.execute("SELECT ts.insertsite(_sitename := %(sitename)s, _east := %(ew)s, _north := %(ns)s, _west := %(ew)s, _south := %(ns)s)",
                {'sitename': sitenameDict[0].get('values')[0], 'ew': coords[1], 'ns': coords[0]})
    siteid = cur.fetchone()[0]
    return siteid
