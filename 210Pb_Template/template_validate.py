"""_Validate 210Pb csv Files_
   Assumes there is a `data` folder from which the python script is run.
   The script obtains all `csv` files in ./data and then reads through
   each of them, validating each field to ensure they are acceptable for
   valid upload.
"""

import glob
import sys
import json
import os
import psycopg2 
import inspect
import neotomaUploader as nu
import pandas as pd

# Obtain arguments and parse them to handle command line arguments
args = nu.parseArguments()

# Connect to the database.
with open('connect_remote.json', mode = "r", encoding = "UTF-8") as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout = 5)
cur = conn.cursor()

filenames = glob.glob(args['data'] + "*.csv")

for filename in filenames:
    print(filename)
    logfile = []

    hashcheck = nu.hashFile(filename)
    filecheck = nu.checkFile(filename)
    logfile = logfile + hashcheck['message'] + filecheck['message']
    
    if hashcheck['pass'] and filecheck['pass']:
        print("  - File is correct and hasn't changed since last validation.")
    else:
        # Load the yml template as a dictionary
        yml_dict = nu.ymlToDict(yml_file=args['yml'])
        yml_data = yml_dict['metadata']
 
        # Obtain the unitcols and units to be used
        vocab_ = nu.vocabDict(yml_data)

        # Verify that the CSV columns and the YML keys match
        csvValid= nu.csvValidator(filename=filename, 
                                  yml_dict=yml_data)
        # Log if the file is valid
        logfile = logfile + csvValid

        testset = dict()
        # Loads CSV file
        df = pd.read_csv(filename)
        
        # Testing Data Units:
        unittest = nu.validUnits(df, vocab_)
        logfile.append('=== Checking Template Unit Definitions ===')
        testset['units'] = unittest['pass']
        logfile = logfile + unittest['message']
    
        ########### Testing site coordinates:
        #sitename
        logfile.append('=== Checking Against Current Sites ===')
        # removed hemisphere = ["NW"], added a note on which hemisphere the site would be.
        sitecheck = nu.validSite(cur = cur, 
                                 yml_dict = yml_data, 
                                 df = df,
                                 sites_str = 'ndb.sites.sitename')
        testset['sites'] = sitecheck['pass']
        logfile = logfile + sitecheck['message']

        ########### Collection Date
        # colldate
        logfile.append('=== Checking Against Collection Date Format ===')
        # format is retrieved in validDate via the yml
        dateCheck = nu.validDate(yml_data, 
                                 df, 
                                 'ndb.collectionunits.colldate')
        logfile = logfile + dateCheck['message']
        testset['date'] = dateCheck['pass']
        
        ########### Collection Units
        logfile.append('=== Checking Against Collection Units ===')
        nameCheck = nu.validCollUnit(cur,
                                     df,
                                     yml_data,
                                     'ndb.sites.geom',
                                     'ndb.collectionunits.handle')
        logfile = logfile + nameCheck['message']
        testset['colunits'] = nameCheck['pass']

        ########### Geopolitical unit:
        logfile.append('=== Checking Against Geopolitical Units ===')
        # Commenting for now so that I can run the script
        # namecheck = nu.validGeoPol(cur, geog, coords)
        #logfile = logfile + namecheck['message']
        #testset['geopol'] = namecheck['pass']

        ########### PI names:
        logfile.append('=== Checking Against Dataset PI Name ===')
        namecheck = nu.validAgent(cur, 
                                  df, 
                                  yml_data, 
                                  'ndb.contacts.contactname')
        logfile = logfile + namecheck['message']

        ########### Age Modeller Name
        logfile.append('=== Checking Against Age Modeller Name(s) ===')
        namecheck = nu.validAgent(cur, 
                                  df, 
                                  yml_data, 
                                  'ndb.chronologies.contactid')
        logfile = logfile + namecheck['message']

        ########### Analyst Name
        logfile.append('=== Checking Against Analyst Name(s) ===')
        namecheck = nu.validAgent(cur, 
                                  df, 
                                  yml_data, 
                                  'ndb.sampleanalysts.contactid')
        logfile = logfile + namecheck['message']

        ########### Make sure the dating horizon is in the analysis units:
        logfile.append('=== Checking the Dating Horizon is Valid ===')
        horizoncheck = nu.validHorizon(df,
                                       yml_data,
                                       'ndb.analysisunits.depth',
                                       'ndb.leadmodels.datinghorizon')
        testset['datinghorizon'] = horizoncheck['pass']
        logfile = logfile + horizoncheck['message']

        ########### Write to log.
        with open(filename + '.log', 'w', encoding = "utf-8") as writer:
            for i in logfile:
                writer.write(i)
                writer.write('\n')