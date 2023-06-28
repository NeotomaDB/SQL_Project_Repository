import json
import psycopg2
from dotenv import load_dotenv
import neotomaUploader as nu
import os

load_dotenv()

data = json.loads(os.getenv('PGDB_HOLDING'))

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = nu.parseArguments()

if args.get('data') == 1:
    filename = 'data/Speckled Trout 2006 GRPO.csv'
else:
    filename = 'data/Speckled Trout 2006 GRPO.csv'

logfile = []
hashcheck = nu.hashFile(filename)
filecheck = nu.checkFile(filename)

if hashcheck['pass'] is False and filecheck['pass'] is False:
    csv_template = nu.read_csv(filename)
    logfile.append("File must be properly validated before it can be uploaded.")
else:
    csv_template = nu.read_csv(filename)
    # This possibly needs to be fixed. How do we know that there is one or more header rows?

uploader = {}

yml_dict = nu.ymlToDict(yml_file=args['yml'])
yml_data = yml_dict['metadata']

# Verify that the CSV columns and the YML keys match
csvValid = nu.csvValidator(filename = filename,
                            yml_data = yml_data)

# Cleaning fields to unique values:
geog = nu.cleanCol('Location', csv_template)
piname = nu.cleanCol('Principal.Investigator.s.', csv_template)
analystname = nu.cleanCol('Analyst', csv_template)
modelername = nu.cleanCol('Modeler', csv_template)
pubname = nu.cleanCol('Publications', csv_template)
collunits = nu.cleanCol('Core.number.or.code', csv_template)
colldate = nu.cleanCol('Date.of.core.collection', csv_template)
location = nu.cleanCol('Coordinate.precision', csv_template)
depths = nu.cleanCol('Depth', csv_template, False)
thicks = nu.cleanCol('Thickness', csv_template, False)
dateunits = nu.cleanCol('X210Pb.Date.Units', csv_template)
ages = nu.cleanCol('X210Pb.Date', csv_template, False)
ageerror = nu.cleanCol('Error..210Pb.Date.', csv_template, False)
agemodel = nu.cleanCol('X210.LeadModel', csv_template)
chronnotes = nu.cleanCol('X210.Lead.Model.Notes', csv_template)
datasetname = nu.cleanCol('Core.number.or.code', csv_template)

dthick = []
# We need to arrange the depths, thicknesses and ages.
for i, value in enumerate(depths):
    dthick.append({'depth': value,
                   'thickness': thicks[i],
                   'age': ages[i],
                   'error': ageerror[i]})

logfile.append('=== Inserting new Site ===')
uploader['siteid'] = nu.insert_site(cur = cur,
                                   yml_dict = yml_dict,
                                   csv_template = csv_template)

logfile.append('siteid: %s' % uploader['siteid'])

# logfile.append('=== Inserting Site Geopol ===')
# # uploader['geopolid'] = nu.insertGeoPol(cur = cur, uploader = uploader)
# # logfile.append('Geopolitical Unit: %s' % uploader['geopolid'])

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = nu.insertCollUnit(cur = cur,
                                           yml_dict = yml_dict,
                                           csv_template = csv_template,
                                           uploader = uploader)

logfile.append('collunitid: %s' % uploader['collunitid'])

logfile.append('=== Inserting Analysis Units ===')
uploader['anunits'] = nu.insertAnalysisUnit(cur = cur,
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