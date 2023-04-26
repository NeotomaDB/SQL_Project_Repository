def validHorizon(depths, horizon):
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
