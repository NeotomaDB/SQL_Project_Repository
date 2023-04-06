def insertSite(cur, sitename, coords):
    """_Insert a site to Neotoma_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        sitename (_list_): _A list returned by the function cleanCol()_
        coords (_list_): _A list returned by the function cleanCol()_

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """
    try:
        assert len(sitename) == 1
    except AssertionError:
        logging.error("Only one single site name should be returned.", exc_info=True)
    try:
        coords = list(map(lambda x: float(x), coords[0].split(',')))
        assert len(coords) == 2
        assert coords[0] >= 0 and coords[0] <= 90
        assert coords[1] <= 0 and coords[1] >= -180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG'.")
    sitename = sitename[0]       
    cur.execute("SELECT ts.insertsite(_sitename := %(sitename)s, _east := %(ew)s, _north := %(ns)s, _west := %(ew)s, _south := %(ns)s)",
                {'sitename': sitename, 'ew': coords[1], 'ns': coords[0]})
    siteid = cur.fetchone()[0]
    return siteid
