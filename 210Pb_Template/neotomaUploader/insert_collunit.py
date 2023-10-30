import logging
from .pull_params import pull_params

def insert_collunit(cur, yml_dict, csv_template, uploader):
    """_Insert a new collection unit to a site_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma 
            Paleoecology Database._
        yml_dict (_dict_): _A `dict` returned by the YAML template._
        csv_template (_dict_): _The csv file with the required data to be uploaded._
        uploader (_dict_): A `dict` object that contains critical information about the
          object uploaded so far.

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """
    try:
        # Here we're just checking to make sure that we do have a site coordinate
        # and geometry.
        assert all(element in [d.get('neotoma') for d in yml_dict.get('metadata')]
                   for element in ['ndb.collectionunits.handle'])
    except AssertionError:
        logging.error("The template must contain a collectionunit handle.", exc_info = True)
    params = ["handle", "colltypeid", "depenvtid", "collunitname", "colldate", "colldevice",
                "gpslatitude", "gpslongitude", "gpsaltitude", "gpserror", 
                "waterdepth", "substrateid", "slopeaspect", "slopeangle", "location", "notes", "geog"]
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.collectionunits')
    cur.execute("""
        SELECT ts.insertcollectionunit(
            _handle := %(handle)s,
            _collunitname := %(collunitname)s,
            _siteid := %(siteid)s, 
            _colltypeid := 3,
            _depenvtid := 19,
            _colldate := %(colldate)s,
            _location := %(location)s,
            _gpslatitude := %(ns)s, _gpslongitude := %(ew)s)""",
    inputs)
    collunitid = cur.fetchone()[0]
    return collunitid