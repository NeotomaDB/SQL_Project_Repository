import json
import psycopg2
from dotenv import load_dotenv
import neotomaUploader as nu
import os

load_dotenv()

data = json.loads(os.getenv('PGDB_LOCAL'))

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = nu.parse_arguments()

if args.get('data') == 1:
    FILENAME = 'data/Speckled Trout 2006 GRPO.csv'
else:
    FILENAME = 'data/Speckled Trout 2006 GRPO.csv'

logfile = []
hashcheck = nu.hash_file(FILENAME)
filecheck = nu.check_file(FILENAME)

if hashcheck['pass'] is False and filecheck['pass'] is False:
    csv_template = nu.read_csv(FILENAME)
    logfile.append("File must be properly validated before it can be uploaded.")
else:
    csv_template = nu.read_csv(FILENAME)
    # This possibly needs to be fixed. How do we know that there is one or more header rows?

uploader = {}

yml_dict = nu.ymlToDict(yml_file=args['yml'])
yml_data = yml_dict['metadata']

# Verify that the CSV columns and the YML keys match
csvValid = nu.csv_validator(filename = FILENAME,
                            yml_data = yml_data)

logfile.append('=== Inserting new Site ===')
uploader['siteid'] = nu.insert_site(cur = cur,
                                   yml_dict = yml_dict,
                                   csv_template = csv_template)

logfile.append(f"siteid: {uploader['siteid']}")

# logfile.append('=== Inserting Site Geopol ===')
# # uploader['geopolid'] = nu.insertGeoPol(cur = cur, uploader = uploader)
# # logfile.append('Geopolitical Unit: %s' % uploader['geopolid'])

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = insert_collunit(cur = cur,
                                           yml_dict = yml_dict,
                                           csv_template = csv_template,
                                           uploader = uploader)

logfile.append(f"collunitid: {uploader['collunitid']}")

logfile.append('=== Inserting Analysis Units ===')
uploader['anunits'] = nu.insert_analysisunit(cur = cur,
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)

# logfile.append('=== Inserting Chronology ===')
# uploader['chronology'] = nu.insertChronology(cur = cur,
#                                             yml_dict = yml_dict,
#                                             csv_template = csv_template,
#                                             uploader = uploader)

#                                             #(cur = cur, 
#                                         collunitid = uploader['collunitid'],
#                                         agetype = agetype[1], 
#                                         agemodel = agemodel[0],
#                                         ages = ages,
#                                         contactname = modelername,
#                                         default = True,
#                                         chronologyname = 'Default 210Pb')

# logfile.append('=== Inserting Chroncontrol ===')
# uploader['chroncontrol'] = nu.insertChroncontrol(cur = cur,
#                                         collunitid = uploader['collunitid'],
#                                         agetype = agetype[1],
#                                         agemodel = agemodel[0],
#                                         ages = ages,
#                                         contactname = modelername,
#                                         default = True,
#                                         chronologyname = 'Default 210Pb')

# uploader['datasetid'] = nu.insertDataset(cur, uploader['collunitid'], datasetname)

# uploader['datasetpi'] = nu.insertDatasetPI(cur, uploader['datasetid'], piname[i], i + 1)

# uploader['processor'] = nu.insertDatasetProcessor(cur, uploader['datasetid'])

# uploader['repository'] = nu.insertDatasetRepository(cur, uploader['datasetid'])

# nu.insertDatasetDatabase(cur, uploader['datasetid'], "")
# nu.insertSamples(cur, ts.insertsample
# ts.insertsampleanalyst
# ts.insertsampleage
# ts.insertdata

# conn.commit()
print(logfile)
conn.rollback()