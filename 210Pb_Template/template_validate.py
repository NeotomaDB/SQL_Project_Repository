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
        dict1 = nu.ymlToDict(yml_file=args['yml'])

        # Obtain the unitcols and units to be used
        unitcols, units = nu.vocabDict(dict1=dict1)

        # Verify that the CSV columns and the YML keys match
        csvValid= nu.csvValidator(filename=filename, units=units, dict1=dict1)
        # Log if the file is valid
        logfile = logfile + csvValid

        # Retrieve the required columns from the YML
        reqCols = nu.getRequiredCols(dict1=dict1)
        
        # Sets up the testset using the yml - still not using this
        testset = {index: False for index in reqCols}
        # This does not belong in the YML template
        testset['units'] = False
     
        # Loads CSV file
        df = pd.read_csv(filename)
        # Convert to a dict of records to validate the entries/units are correct
        csv_template = df.to_dict('records')
       
       ## May be able to remove this
        # Retrieves each column's unique values (vs cleanCol):
        colsDict = {}
        for col in reqCols:
            colsDict[col] = list(df[col].unique())

        # Testing Data Units:
        unittest = nu.validUnits(csv_template, unitcols, units)
        logfile.append('=== Checking Template Unit Definitions ===')
        testset['units'] = unittest['pass']
        logfile = logfile + unittest['message']

        ########### Testing site coordinates:
        #sitename
        #print(colsDict)
        logfile.append('=== Checking Against Current Sites ===')
        #sitecheck = nu.validSite(cur, colsDict['Geographic.coordinates'], 
        #                              hemisphere = ["NW"], sitename = colsDict['Site.name'][0])
        sitecheck = nu.validSite(cur, dict1['metadata'], df)
        testset['sites'] = sitecheck['pass']
        logfile = logfile + sitecheck['message']

        ########### Collection Date
        # colldate
        logfile.append('=== Checking Against Collection Date Format ===')
        dateCheck = nu.validDate(date = colsDict['Date.of.core.collection'], 
                                 format = '%Y-%m-%d')
        logfile = logfile + dateCheck['message']
        testset['date'] = dateCheck['pass']
        
        ########### Collection Units
        logfile.append('=== Checking Against Collection Units ===')
        nameCheck = nu.validCollUnit(cur, 
                                     colsDict['Geographic.coordinates'], 
                                     colsDict['Core.number.or.code'])
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
                                  dict1['metadata'], 
                                  'ndb.contacts.contactname')
        logfile = logfile + namecheck['message']

        ########### Age Modeller Name
        logfile.append('=== Checking Against Age Modeller Name(s) ===')
        namecheck = nu.validAgent(cur, 
                                  df, 
                                  dict1['metadata'], 
                                  'ndb.chronologies.contactid')
        logfile = logfile + namecheck['message']

        ########### Analyst Name
        logfile.append('=== Checking Against Analyst Name(s) ===')
        namecheck = nu.validAgent(cur, 
                                  df, 
                                  dict1['metadata'], 
                                  'ndb.sampleanalysts.contactid')
        logfile = logfile + namecheck['message']

        ########### Make sure the dating horizon is in the analysis units:
        logfile.append('=== Checking the Dating Horizon is Valid ===')
        horizoncheck = nu.validHorizon(colsDict['Depth'], 
                                       colsDict['X210Pb.dating.horizon'])
        testset['datinghorizon'] = horizoncheck['pass']
        logfile = logfile + horizoncheck['message']

        ########### Write to log.
        with open(filename + '.log', 'w', encoding = "utf-8") as writer:
            for i in logfile:
                writer.write(i)
                writer.write('\n')