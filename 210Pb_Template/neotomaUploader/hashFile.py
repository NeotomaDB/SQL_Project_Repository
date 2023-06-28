import hashlib
import os

def hashFile(filename):
    response = {'pass': False, 'hash': None, 'message': []}
    logfile = filename + '.log'
    response['hash'] = hashlib.md5(open(filename,'rb').read()).hexdigest()
    response["message"].append(response['hash'])
    if os.path.exists(logfile):
        with open(logfile) as f:
            hashline = f.readline().strip('\n')
        if hashline == response['hash']:
            response['pass'] = True
            response['message'].append("Hashes match, file hasn't changed.")
        else:
            response['message'].append(f"File has changed, validating {filename}.")
    else:
        response['message'].append(f"Validating {filename}.")
    return response
