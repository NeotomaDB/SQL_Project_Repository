import warnings
import logging

def retrieveDict(yml_dict, sqlColumn):
    """_Get Dictionary for a Neotoma column using the YAML template_

    Args:
        yml_dict (_dict_): _The YAML template object imported by the user._
        sqlColumn (_str_): _A character string indicating the SQL column to be matched._

    Returns:
        _object_: _The object associated with a particular YAML template entry_
    """
    #result = next((d['column'] for d in yml_dict if d['neotoma'] == sqlColumn), None)
    # retrieving the dict instead:
    try:
        assert type(yml_dict) is dict
        assert yml_dict.get('metadata')
    except AssertionError:
        logging.error("The yml_dict must be a dict object (not a list) containing the key 'metadata'.", exc_info=True)
    result = next((d for d in yml_dict['metadata'] if d['neotoma'] == sqlColumn), None)
    if result is None:
        warnings.warn("No matching dictionary found.")
    else:
        return result
