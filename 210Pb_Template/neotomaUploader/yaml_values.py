from .retrieve_dict import retrieve_dict
from .clean_column import clean_column

def yaml_values(yml_dict, csv_template, column):
    """_Extract values from CSV file conforming to the YAML dictionary entry_

    Args:
        yml_dict (_dict_): _The YAML dictionary described by the user._
        csv_template (_list_): _A list pulled from a CSV template file defined by the user_
        column (_str_): _A Neotoma table/column defined by the function call._

    Returns:
        _list_: _A list of the same structure as individual elements within yml_dict, with a 'values' field appended._
    """
    pointer = retrieve_dict(yml_dict, column)
    def add_val (x):
        x['values'] = clean_column(x.get('column'),
                               csv_template,
                               clean = not x.get('repeat'))
        return x
    values = [add_val(x) for x in pointer]
    return values
