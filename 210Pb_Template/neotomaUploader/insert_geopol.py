def insert_geopol(cur, yml_dict, csv_template, uploader):
    """_Insert a site's geopolitical unit to Neotoma_

    def insert_geopol(cur, yml_dict, csv_template)

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma 
            Paleoecology Database._
        yml_dict (_dict_): _A `dict` returned by the YAML template._
        csv_template (_dict_): _The csv file with the required data to be uploaded._

    Returns:
        _int_: _The integer value of the newly created siteid from the Neotoma Database._
    """
     
    if 'siteid' in uploader.keys():
        # First test if the site exists.
        isAdded = """SELECT * FROM ap.sitegadm WHERE siteid =  %(siteid)s"""
        cur.execute(isAdded, { 'siteid': uploader['siteid'] })
        result = cur.fetchone()[0]
        if result is None:
            # Inserts site and fid in ap.sitegadm if it didn't exist
            #INSERT INTO ap.sitegadm(siteid, fid)
            assignGeoPol = """
            INSERT INTO ap.sitegadm(siteid, fid)
                (SELECT st.siteid, ga.uid
                       FROM ap.gadm AS ga
                       JOIN ndb.sites AS st ON ST_Covers(ga.shape, st.geog)
                       WHERE st.siteid = %(siteid)s)
                RETURNING fid;
                """        
            cur.execute(assignGeoPol, {'siteid': uploader['siteid']})
            result = cur.fetchone()[0]
    else:
        result = None
    return result