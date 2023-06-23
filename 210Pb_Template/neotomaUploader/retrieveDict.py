import warnings

def retrieveDict(yml_dict, sqlColumn):
    #result = next((d['column'] for d in yml_dict if d['neotoma'] == sqlColumn), None)
    # retrieving the dict instead:
    result = next((d for d in yml_dict if d['neotoma'] == sqlColumn), None)

    if result is None:
        warnings.warn("No matching dictionary found.")
    else:
        return result