import datetime
import logging
from .retrieveDict import retrieveDict
from .cleanCol import cleanCol

def insertCollUnit(cur, yml_dict, csvTemplate, uploader):
    """_Insert a new collection unit to a site_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        sitename (_list_): _A list returned by the function cleanCol()_
        coords (_list_): _A list returned by the function cleanCol()_

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._

    Returns:
        _type_: _description_
    """

    coordsD = retrieveDict(yml_dict, 'ndb.collectionunits.geom')
    collnameD = retrieveDict(yml_dict, 'ndb.collectionunits.handle')
    collDateD = retrieveDict(yml_dict, 'ndb.collectionunits.colldate')
    collLocD = retrieveDict(yml_dict, 'ndb.collectionunits.location')

    coords = cleanCol(coordsD.get('column'),
                               csvTemplate,
                               clean = not coordsD.get('repeat'))

    colldate = cleanCol(collDateD.get('column'),
                               csvTemplate,
                               clean = not collDateD.get('repeat'))

    collunits = cleanCol(collnameD.get('column'),
                               csvTemplate,
                               clean = not collnameD.get('repeat'))
    
    location = cleanCol(collLocD.get('column'),
                               csvTemplate,
                               clean = not collLocD.get('repeat'))

    newdate = datetime.datetime.strptime(colldate[0], '%Y-%m-%d').date()

    handle = collunits[0].upper().replace(' ', '')[0:9]

    try:
        coords = list(map(lambda x: float(x), coords[0].split(',')))
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
