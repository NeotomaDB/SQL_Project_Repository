def cleanCol(column, template, clean = True):
    if clean:
        setlist = list(set(map(lambda x: x[column], template)))
    else:
        setlist = list(map(lambda x: x[column], template))
    return setlist
