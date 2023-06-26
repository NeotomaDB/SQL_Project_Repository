import neotomaUploader as nu

def insertSite(cur, yml_dict, template):
    """_Insert a site to Neotoma_

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
        coordColumn = list(filter(lambda x: x.get('neotoma') == 'ndb.sites.geom', yml_dict.get('metadata')))[0].get('column')
        coords = [float(i) for i in nu.cleanCol(coordColumn, template)[0].split(',')]
        assert len(coords) == 2
        assert coords[0] >= 0 and coords[0] <= 90
        assert coords[1] <= 0 and coords[1] >= -180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG'.")
    siteColumn = list(filter(lambda x: x.get('neotoma') == 'ndb.sites.sitename', yml_dict.get('metadata')))[0].get('column')
    sitename = nu.cleanCol(siteColumn, template)[0]
    cur.execute("SELECT ts.insertsite(_sitename := %(sitename)s, _east := %(ew)s, _north := %(ns)s, _west := %(ew)s, _south := %(ns)s)",
                {'sitename': sitename, 'ew': coords[1], 'ns': coords[0]})
    siteid = cur.fetchone()[0]
    return siteid
