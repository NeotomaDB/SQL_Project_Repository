import datetime
import logging
from .retrieve_dict import retrieve_dict
from .clean_column import clean_column
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
                "waterdepth", "substrateid", "slopeaspect", "slopeangle", "location", "notes"]
    add_unit_inputs = {}
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.collectionunits')
    print(inputs)
    try:
        coords = list(map(float, coords[0].split(',')))
        assert len(coords) == 2
        assert coords[0] >= -90 and coords[0] <= 90
        assert coords[1] >= -180 and coords[1] <= 180
    except AssertionError:
        logging.error("Coordinates are improperly formatted. They must be in the form 'LAT, LONG' [-90 -> 90] and [-180 -> 180].")
    cur.execute("""
        SELECT ts.insertcollectionunit(
            _handle := %(handle)s,
            _collunitname := %(collname)s,
            _siteid := %(siteid)s, 
            _colltypeid := 3,
            _depenvtid := 19,
            _colldate := %(newdate)s,
            _location := %(location)s,
            _gpslatitude := %(ns)s, _gpslongitude := %(ew)s)""",
          {'collname': collunits[0], 'newdate': newdate,
           'siteid' : uploader.get('siteid'),
           'handle': handle, 'location': location[0],
           'ns': coords[0], 'ew': coords[1]})
    collunitid = cur.fetchone()[0]
    return collunitid
