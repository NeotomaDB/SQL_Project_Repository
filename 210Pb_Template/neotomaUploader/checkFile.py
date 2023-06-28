import re
import os

def checkFile(filename):
    """_Validate the existence and result of a logfile._

    Args:
        filename (_str_): _The file path or relative path for a template CSV file._

    Returns:
        _dict_: _A dict type object with properties `pass` (bool), `match` (int) and `message` (str[])._
    """    
    response = {'pass': False, 'match': 0, 'message': []}
    logfile = filename + '.log'
    
    if os.path.exists(logfile):
        error = []
        with open(logfile, "r", encoding="utf-8") as f:
            for line in f:
                error = re.match('✗', line)
                if error:
                    response['match'] = response['match'] + 1
        if response['match'] == 0:
            response['pass'] = True
            response['message'].append("No errors found in the last validation.")
        else:
            response['message'].append("Errors found in the prior validation.")
    else:
        response['message'].append("No prior log file exists.")
    return response