from .yaml_values import yaml_values
from .valid_column import valid_column
import re

def validAgent(cur, csv_template, yml_dict):
    
    """_Get user agent or contact from Neotoma_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        agentname (_string_): _A user name or individual._
    """
    response = { 'pass': False, 'name': None, 'message': [] }
    namematch = []

    pattern = r'(contactid|contactname)'
    agentD = yaml_values(yml_dict, csv_template, pattern)

    for element in agentD:
        response['message'].append(f"=== Checking Against Dataset {element['column']} ===")
        agent_message = valid_column(element)
        agentname = element['values']
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