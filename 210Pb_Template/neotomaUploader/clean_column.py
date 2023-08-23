def clean_column(column, template, clean = True):
    """_cleanCol_

    Args:
        column (_list_): _The name of the column to use_
        template (_list_): _The CSV file as a list of dictionaries_
        clean (bool, optional): _Does the column get reduced to only the unique values?_. Defaults to True.

    Returns:
        _list_: _The cleaned column._
    """
    if clean:
        setlist = list(set(map(lambda x: x[column], template)))
    else:
        setlist = list(map(lambda x: x[column], template))
    return setlist
