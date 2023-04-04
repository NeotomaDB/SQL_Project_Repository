def validunits (template, unitcols, units):
    """_Are the units provided valid based on defined unit names?_

    Args:
        template (_list_): _The csv file content, as a list._
        unitcols (_dict_): _The names of each set of columns listing units in the file, with a key linked to the `units` column._
        units (_dict_): _Acceptable units for each data column type._

    Returns:
        _list_: _A list of columns with invalid units._
    """    
    invalid = []
    for i in unitcols.keys():
        for j in unitcols[i]:
            values = list(set(map(lambda x: x[j], template)))
            values = list(filter(lambda x: x != '', values))
            valid = all([k in units[i] for k in values])
            if valid == False:
                invalid.append(j)
    return invalid

