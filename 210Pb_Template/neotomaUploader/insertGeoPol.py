def insertGeoPol(cur, uploader):
    if 'siteid' in uploader.keys():
        # First test if the site exists.
        isAdded = """SELECT * FROM ap.sitegadm WHERE siteid =  %(siteid)s"""
        cur.execute(isAdded, { 'siteid': uploader['siteid'] })
        result = cur.fetchone()
        if result is None:
            # If the site doesn't already exist:
            assignGeoPol = """
                INSERT INTO ap.sitegadm(siteid, fid)
                (SELECT st.siteid, ga.fid
                FROM ndb.sites AS st
                JOIN ap.gadm_410 AS ga ON ST_Covers(ga.geom, st.geog)
                WHERE st.siteid = %(siteid)s);"""
            cur.execute(assignGeoPol, { 'siteid': uploader['siteid'] })
            result = cur.fetchone()
            if result is not None:
                result = result[0]
    else:
        result = None
    return result
