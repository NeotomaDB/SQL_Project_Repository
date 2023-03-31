def getAgent(cur, agentname):
    """_Get user agent or contact from Neotoma_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        agentname (_string_): _A user name or individual._
    """    
    nameQuery = """
            SELECT ct.contactid
            FROM ndb.contacts AS ct
            WHERE %(name)s = ct.contactname"""
    cur.execute(nameQuery, {'name'})
