from .retrieveDict import retrieveDict
from .validColumn import validColumn, cleanColumn
#def validAgent(cur, agentname):
def validAgent(cur, df, yml_dict, str_contact):
    """_Get user agent or contact from Neotoma_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        agentname (_string_): _A user name or individual._
    """
    response = { 'pass': False, 'name': None, 'message': [] }
    namematch = []
    agentnameD = retrieveDict(yml_dict, str_contact)
    agent_message = validColumn(df, agentnameD)
    agentname = cleanColumn(df, agentnameD)
    if len(agent_message) >0:
        response['message'].append(agent_message)
    
    for name in agentname:
        response['message'].append(f"*** PI: {name} ***")
        nameQuery = """
                SELECT contactid, contactname
                FROM ndb.contacts AS ct
                WHERE to_tsvector(ct.contactname) @@ plainto_tsquery(%(name)s);"""
        cur.execute(nameQuery, {'name': name})
        result = {'name': name, 'match':  cur.fetchall() or []}
        namematch.append(result)
    matches = []
    for person in namematch:
        if len(person['match']) ==0:
            response['message'].append(f"✗ No approximate matches found for {person['name']}. Have they been added to Neotoma?")
            matches.append(False)
        elif any([person['name'] == i[1] for i in person['match']]):
            response['message'].append(f"✔ Exact match found for {person['name']}.")
            matches.append(True)
        else:
            response['message'].append(f"? No exact match found for {person['name']}, several potential matches follow:")
            matches.append(False)
            for i in person['match']:
                response['message'].append(f" * {i[1]}")
    if all(matches):
        response['pass'] = True
    return response