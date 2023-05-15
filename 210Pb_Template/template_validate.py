"""_Validate 210Pb csv Files_
   Assumes there is a `data` folder from which the python script is run.
   The script obtains all `csv` files in ./data and then reads through
   each of them, validating each field to ensure they are acceptable for
   valid upload.
"""
import glob
import sys
import argparse
import json
import psycopg2
import neotomaUploader as nu

# Obtain arguments and parse them to handle command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, help='Path to the data directory')
parser.add_argument('--template', type=str, help='Template to use for evaluation')
args = parser.parse_args()

data_directory = args.data

yml_file = args.template

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = sys.argv

if len(args) > 1:
    filenames = glob.glob(data_directory + "*.csv")
else:
    filenames = glob.glob("data/" + "*.csv")

for filename in filenames:
    
    print(filename)   
    logfile = []

    hashcheck = nu.hashFile(filename)
    filecheck = nu.checkFile(filename)
    logfile = logfile + hashcheck['message'] + filecheck['message']
    
    if hashcheck['pass'] and filecheck['pass']:
       print("  - File is correct and hasn't changed since last validation.")
    else:
        template = nu.read_csv(filename)
        testset = { 'units': False,
                'sites': False,
                'colunits': False,
                'geopol': False,
                'date': False,
                'piname': False,
                'analystname': False,
                'modelername': False,
                'datinghorizon': False}
        
        # Cleaning fields to unique values:
        sitename = nu.cleanCol('Site.name', template)
        coords = nu.cleanCol('Geographic.coordinates', template)
        geog = nu.cleanCol('Location', template)
        piname = nu.cleanCol('Principal.Investigator.s.', template)
        analystname = nu.cleanCol('Analyst', template)
        modelername = nu.cleanCol('Modeler', template)
        pubname = nu.cleanCol('Publications', template)
        collunits = nu.cleanCol('Core.number.or.code', template)
        depths = nu.cleanCol('Depth', template)
        datinghorizon = nu.cleanCol('X210Pb.dating.horizon', template)
        colldate = nu.cleanCol('Date.of.core.collection', template)

        # Template validate
        dict1 = nu.ymlToDict(yml_file=yml_file)
        
        unitcols, units = nu.vocabDict(dict1=dict1)
        
        my_list= nu.csvValidator(filename=filename, units=units, dict1=dict1)
        logfile = logfile + my_list 

        # Testing Data Units:
        unittest = nu.validUnits(template, unitcols, units)
        logfile.append('=== Checking Template Unit Definitions ===')
        testset['units'] = unittest['pass']
        logfile = logfile + unittest['message']

        ########### Testing site coordinates:
        logfile.append('=== Checking Against Current Sites ===')
        sitecheck = nu.validSite(cur, coords, hemisphere = ["NW"], sitename = sitename[0])
        testset['sites'] = sitecheck['pass']
        logfile = logfile + sitecheck['message']

        ########### Collection Date
        logfile.append('=== Checking Against Collection Date Format ===')
        dateCheck = nu.validDate(date = colldate, format = '%Y-%m-%d')
        logfile = logfile + dateCheck['message']
        testset['date'] = dateCheck['pass']
        
        ########### Collection Units
        logfile.append('=== Checking Against Collection Units ===')
        nameCheck = nu.validCollUnit(cur, coords, collunits)
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
        namecheck = nu.validAgent(cur, piname)
        logfile = logfile + namecheck['message']

        ########### Age Modeller Name
        logfile.append('=== Checking Against Age Modeller Name(s) ===')
        namecheck = nu.validAgent(cur, modelername)
        logfile = logfile + namecheck['message']

        ########### Analyst Name
        logfile.append('=== Checking Against Analyst Name(s) ===')
        namecheck = nu.validAgent(cur, analystname)
        logfile = logfile + namecheck['message']

        ########### Make sure the dating horizon is in the analysis units:
        logfile.append('=== Checking the Dating Horizon is Valid ===')
        horizoncheck = nu.validHorizon(depths, datinghorizon)
        testset['datinghorizon'] = horizoncheck['pass']
        logfile = logfile + horizoncheck['message']
        
        ########### Write to log.
        with open(filename + '.log', 'w', encoding = "utf-8") as writer:
            for i in logfile:
                writer.write(i)
                writer.write('\n')