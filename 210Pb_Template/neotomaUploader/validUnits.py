def validUnits (template, unitcols, units):
    """_Are the units provided valid based on defined unit names?_
    We pass in two dictionaries, that are expected to have matching keys in the dicts.
    For each key in `unitcols` (the columns in the template that contain units) we then
    have a key in `units` that contains the valid units for that column.

    Args:
        template (_list_): _The csv file content, as a list._
        unitcols (_dict_): _The names of each set of columns listing units in the file, with a key linked to the `units` column._
        units (_dict_): _Acceptable units for each data column type._

    Returns:
        _list_: _A list of columns with invalid units._
    """    
    response = { 'pass': False, 'message': [] }
    for i in unitcols.keys():
        for j in unitcols[i]:
            values = list(set(map(lambda x: x[j], template)))
            values = list(filter(lambda x: x != '', values))
            valid = all([k in units[i] for k in values])
            if valid == False:
                response['message'].append(f"✗ Column {i} contains units that do not follow the expected set.")
    if len(response['message']) == 0:
        response['pass'] = True
        response['message'].append(f"✔ All units validate.")
    return response

