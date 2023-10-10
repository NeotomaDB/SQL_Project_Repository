"""_Validate 210Pb csv Files_
   Assumes there is a `data` folder from which the python script is run.
   The script obtains all `csv` files in ./data and then reads through
   each of them, validating each field to ensure they are acceptable for
   valid upload.
"""

import glob
import json
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import neotomaUploader as nu

# Obtain arguments and parse them to handle command line arguments
args = nu.parse_arguments()

load_dotenv()

#data = json.loads(os.getenv('PGDB_HOLDING'))
data = json.loads(os.getenv('PGDB_LOCAL'))


conn = psycopg2.connect(**data, connect_timeout = 5)
cur = conn.cursor()

filenames = glob.glob(args['data'] + "*.csv")

for filename in filenames:
    print(filename)
    logfile = []

    hashcheck = nu.hash_file(filename)
    filecheck = nu.check_file(filename)
    logfile = logfile + hashcheck['message'] + filecheck['message']

    if hashcheck['pass'] and filecheck['pass']:
        print("  - File is correct and hasn't changed since last validation.")
    else:
        # Load the yml template as a dictionary
        yml_dict = nu.yml_to_dict(yml_file=args['yml'])
        yml_data = yml_dict['metadata']

        # Obtain the unitcols and units to be used
        vocab_ = nu.vocabDict(yml_data)

        # Verify that the CSV columns and the YML keys match
        csvValid = nu.csv_validator(filename = filename,
                                   yml_data = yml_data)
        # Log if the file is valid
        logfile = logfile + csvValid

        testset = {}
        # Loads CSV file
        df = pd.read_csv(filename)
        csv_template = nu.read_csv(filename)

        # Testing Data Units:
        unittest = nu.validUnits(df, vocab_)
        logfile.append('=== Checking Template Unit Definitions ===')
        testset['units'] = unittest['pass']
        logfile = logfile + unittest['message']
        ########## Testing site coordinates:
        # sitename
        logfile.append('=== Checking Against Current Sites ===')
        sitecheck = nu.valid_site(cur = cur,
                                 yml_dict = yml_dict,
                                 csv_template = csv_template)
        testset['sites'] = sitecheck['pass']
        logfile = logfile + sitecheck['message']

        ########### Collection Date
        # colldate
        logfile.append('=== Checking All Date Formats ===')
        # format is retrieved in validDate via the yml
        dateCheck = nu.valid_date(yml_dict,
                                csv_template)
        logfile = logfile + dateCheck['message']
        testset['date'] = dateCheck['pass']

        ########### Collection Units
        logfile.append('=== Checking Against Collection Units ===')
        nameCheck = nu.valid_collectionunit(cur,
                                    yml_dict,
                                    csv_template)
        logfile = logfile + nameCheck['message']
        testset['colunits'] = nameCheck['pass']
        
        ########### Geopolitical unit:
        #logfile.append('=== Checking Against Geopolitical Units ===')
        # Commenting for now so that I can run the script
        # namecheck = nu.validGeoPol(cur, geog, coords)
        #logfile = logfile + namecheck['message']
        #testset['geopol'] = namecheck['pass']

        ########### PI names:
        logfile.append('=== Checking Against Contact Names ===')
        namecheck = nu.valid_agent(cur,
                                  csv_template,
                                  yml_dict)
        logfile = logfile + namecheck['message']

        ########### Make sure the dating horizon is in the analysis units:
        logfile.append('=== Checking the Dating Horizon is Valid ===')
        horizoncheck = nu.valid_horizon(yml_dict,
                                       csv_template)
        testset['datinghorizon'] = horizoncheck['pass']
        logfile = logfile + horizoncheck['message']

        ########### Taxa names:
        logfile.append('=== Checking Against Taxa Names ===')
        namecheck = nu.valid_taxa(cur,
                                  csv_template,
                                  yml_dict)
        logfile = logfile + namecheck['message']

        ########### Write to log.
        with open(filename + '.log', 'w', encoding = "utf-8") as writer:
            for i in logfile:
                writer.write(i)
                writer.write('\n')