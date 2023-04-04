import datetime

def validDate(inputdate, format):
    """_Check to see if the date format is valid for a given type_

    Args:
        inputdate (_array_): _An array of dates_
        format (_string_): _A string representing the POSIX date/time format for the expected input dates._

    Returns:
        _dict_: _An object with a valid parameter and the re-formatted date (as a datetime object)._
    """
    if format is None:
        format = '%Y-%m-%d'
    try:
        newdate = datetime.datetime.strptime(inputdate[0], '%Y-%m-%d').date()
    except ValueError:
        return {'valid': False, 'date': 'Expected date format is YYYY-mm-dd'}
    return {'valid': True, 'date': newdate}
