from .retrieveColumn import retrieveColumn
import datetime

#def validDate(date, format):
def validDate(yml_dict, df, date_str):
    """_Check to see if the date format is valid for a given type_

    Args:
        inputdate (_array_): _An array of dates_
        format (_string_): _A string representing the POSIX date/time format for the expected input dates._

    Returns:
        _dict_: _An object with a valid parameter and the re-formatted date (as a datetime object)._
    """
    date_dict = retrieveColumn(yml_dict, date_str)
    date = date_dict['column']
    date = list(df[date].unique())
    format = date_dict['format']

    response = {'pass': False, 'date': date, 'message': []}
    if format is None:
        format = '%Y-%m-%d'
    try:
        newdate = datetime.datetime.strptime(date[0], format).date()
        response['message'].append(f"✔ Date {newdate} looks good!")
    except ValueError:
        response['message'].append(f"✗ Expected date format is {format}")
    return response
