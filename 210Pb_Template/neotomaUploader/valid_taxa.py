from .valid_column import valid_column
from .yaml_values import yaml_values

def valid_taxa(cur, csv_template, yml_dict):
    """_Get taxa content from Neotoma_

    Args:
        cur (_psycopg2.extensions.cursor_): _A cursor pointing to the Neotoma Paleoecology Database._
        csv_template (_string_): _A taxa name._
        yml_dict (_dict_): _The dictionary object passed by yml_to_dict._
    """
    
    response = { 'pass': False, 'name': None, 'message': [] }

    pattern = r'(values)'
    taxa_dict = yaml_values(yml_dict, csv_template, pattern)

    for element in taxa_dict:
        response['message'].append(f"  === Checking Against Taxa {element['column']} ===")
        taxa_message = valid_column(element)
        taxonname = element['taxonname']
        taxamatch = []
        if len(taxa_message) > 0:
            response['message'].append(taxa_message)
 
        response['message'].append(f"  *** Named Taxa: {taxonname} ***")
        nameQuery = """
                SELECT taxonid, taxonname
                FROM ndb.taxa AS tx
                WHERE to_tsvector(tx.taxonname) @@ plainto_tsquery(%(taxonname)s);"""
        cur.execute(nameQuery, {'taxonname': taxonname})
        result = {'name': taxonname, 'match':  cur.fetchall() or []}
        taxamatch.append(result)
 
        matches = []
        for taxon in taxamatch:
            if len(taxon['match']) ==0:
                response['message'].append(f"  ✗ No approximate matches found for {taxon['name']}. Have they been added to Neotoma?")
                matches.append(False)
            elif any([taxon['name'] == i[1] for i in taxon['match']]):
                response['message'].append(f"  ✔ Exact match found for {taxon['name']}.")
                matches.append(True)
            else:
                response['message'].append(f"  ? No exact match found for {taxon['name']}, several potential matches follow:")
                matches.append(False)
                for i in taxon['match']:
                    response['message'].append(f"   * {i[1]}")
        if all(matches):
            response['pass'] = True
    return response