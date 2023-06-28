from .retrieveDict import retrieveDict
from .valid_column import valid_column, cleanColumn
def validHorizon(df, yml_dict, depth_str, horizon_str):
    """_Is the dated horizon one of the accepted dates?_

    Args:
        depths (_array_): _An array of numbers representing depths in the core._
        horizon (_array_): _An array of length 1 for the 210 Dating horizon_

    Returns:
        _dict_: _A dict with the validity and an index of the matched depth._
    """
    response = {'pass': False,
                'index': [],
                'message': []}
    depthD = retrieveDict(yml_dict, depth_str)
    depth_message = valid_column(df, depthD)
    depths = cleanColumn(df, depthD)
    if len(depth_message) >0:
        response['message'].append(depth_message)

    horizonD = retrieveDict(yml_dict, horizon_str)
    horizon_message = valid_column(df, horizonD)
    horizon = cleanColumn(df, horizonD)
    if len(horizon_message) >0:
        response['message'].append(horizon_message)

    if len(horizon) == 1:
        matchingdepth = [i == horizon[0] for i in depths]
        if any(matchingdepth):
            response['pass'] = True
            response['index'] = next(i for i,v in enumerate(matchingdepth) if v)
            response['message'].append("✔  The dating horizon is in the reported depths.")
        else:
            response['pass'] = False
            response['index'] = -1
            response['message'].append("✗  There is no depth entry for the dating horizon in the 'depths' column.")
    else:
        response['pass'] = False
        response['index'] = None
        if len(horizon) > 1:
            response['message'].append("✗  Multiple dating horizons are reported.")
        else:
            response['message'].append("✗  No dating horizon is reported.")
    return response