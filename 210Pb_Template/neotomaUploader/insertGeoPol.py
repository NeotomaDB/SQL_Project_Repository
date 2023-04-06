def insertGeoPol(cur, siteid):
    isAdded = """SELECT * FROM ap.sitegadm WHERE siteid =  %(siteid)s"""
    cur.execute(isAdded, {'siteid': siteid})
    result = cur.fetchone()[1]
    if result is None:
        assignGeoPol = """
            INSERT INTO ap.sitegadm(siteid, fid)
            (SELECT st.siteid, ga.fid
            FROM ndb.sites AS st
            JOIN ap.gadm_410 AS ga ON ST_Covers(ga.geog, st.geog)
            WHERE st.siteid = %(siteid)s);"""
        cur.execute(assignGeoPol, {'siteid': siteid})
        result = cur.fetchone()[1]
    return result
