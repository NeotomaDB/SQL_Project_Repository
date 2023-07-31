from .retrieveDict import retrieveDict
from .yaml_values import yaml_values
import datetime
import re

def valid_date(yml_dict, csv_template):
    """_Check to see if the date format is valid for a given type_

    Args:
        yml_dict (_dict_): _An array of dates_
        csv_template (_string_): _A string representing the POSIX date/time format for the expected input dates._

    Returns:
        _dict_: _An object with a valid parameter and the re-formatted date (as a datetime object)._
    """
    response = {'pass': False, 'message': []}
    pattern = r'(date)'
    dateD = yaml_values(yml_dict, csv_template, pattern)
    for i in dateD:
        try:
            date_set = i.get('values')
            new_date = [datetime.datetime.strptime(j, i['format']).date() for j in date_set]
            response['message'].append(f"✔ Dates for {i.get('neotoma')} looks good!")
        except ValueError:
            response['message'].append(f"✗ Expected date format is {format}")
    return response