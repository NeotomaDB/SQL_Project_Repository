def validHorizon(depths, horizon):
    """_Is the dated horizon one of the accepted dates?_

    Args:
        depths (_array_): _An array of numbers representing depths in the core._
        horizon (_array_): _An array of length 1 for the 210 Dating horizon_

    Returns:
        _dict_: _A dict with the validity and an index of the matched depth._
    """
    if len(horizon) == 1:
        matchingdepth = [i == horizon[0] for i in depths]
        if any(matchingdepth):
            valid = True
            hmatch = { 'index': next(i for i,v in enumerate(matchingdepth) if v) }
        else:
            valid = False
            hmatch = { 'index': -1 }
    else:
        valid = False
        hmatch = { 'index': None }
    return {'valid': valid, 'index': hmatch}
