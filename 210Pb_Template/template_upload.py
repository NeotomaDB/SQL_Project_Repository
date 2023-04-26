import sys
import json
import psycopg2
import neotomaUploader as nu

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = sys.argv

if len(args) > 1:
    filename = args[1]
else:
    filename = 'data/Speckled Trout 2006 GRPO.csv'

logfile = []
hashcheck = nu.hashFile(filename)
filecheck = nu.checkFile(filename)

if hashcheck['pass'] == False and filecheck['pass'] == False:
    logfile.append("File must be properly validated before it can be uploaded.")
else:
    template = nu.read_csv(filename)
    del template[0]
    del template[0]
    
uploader = {}

# Cleaning fields to unique values:
sitename = nu.cleanCol('Site.name', template)
coords = nu.cleanCol('Geographic.coordinates', template)
geog = nu.cleanCol('Location', template)
piname = nu.cleanCol('Principal.Investigator.s.', template)
analystname = nu.cleanCol('Analyst', template)
modelername = nu.cleanCol('Modeler', template)
pubname = nu.cleanCol('Publications', template)
collunits = nu.cleanCol('Core.number.or.code', template)
colldate = nu.cleanCol('Date.of.core.collection', template)
location = nu.cleanCol('Coordinate.precision', template)
depths = nu.cleanCol('Depth', template, False)
thicks = nu.cleanCol('Thickness', template, False)
dateunits = nu.cleanCol('X210Pb.Date.Units', template)
ages = nu.cleanCol('X210Pb.Date', template, False)
ageerror = nu.cleanCol('Error..210Pb.Date.', template, False)
agemodel = nu.cleanCol('X210.LeadModel', template)
chronnotes = nu.cleanCol('X210.Lead.Model.Notes', template)
datasetname = nu.cleanCol('Core.number.or.code', template)

dthick = []
# We need to arrange the depths, thicknesses and ages.
for i in range(len(depths)):
    dthick.append({'depth': depths[i], 'thickness': thicks[i], 'age': ages[i], 'error': ageerror[i]})

logfile.append('=== Inserting new Site ===')
uploader['siteid'] = nu.insertSite(cur = cur, sitename = sitename, coords = coords)
logfile.append('siteid: %s' % uploader['siteid'])

logfile.append('=== Inserting Site Geopol ===')
uploader['geopolid'] = nu.insertGeoPol(cur = cur, siteid = uploader['siteid'])
logfile.append('Geopolitical Unit: %s' % uploader['geopolid'])

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = nu.insertCollUnit(cur = cur, collunits = collunits, 
                                        colldate = colldate, siteid = uploader['siteid'],
                                        coords = coords, location = location)
logfile.append('collunitid: %s' % uploader['collunitid'])

logfile.append('=== Inserting Analysis Units ===')
uploader['anunits'] = nu.insertAnalysisUnit(cur = cur,
                                        collunitid = uploader['collunitid'],
                                        dthick = dthick)

logfile.append('=== Inserting Chronology ===')
uploader['chronology'] = nu.insertChronology(cur = cur, 
                                        collunitid = uploader['collunitid'],
                                        agetype = agetype[1], 
                                        agemodel = agemodel[0],
                                        ages = ages,
                                        contactname = modelername,
                                        default = True,
                                        chronologyname = 'Default 210Pb')

logfile.append('=== Inserting Chroncontrol ===')
uploader['chroncontrol'] = nu.insertChroncontrol(cur = cur, 
                                        collunitid = uploader['collunitid'],
                                        agetype = agetype[1], 
                                        agemodel = agemodel[0],
                                        ages = ages,
                                        contactname = modelername,
                                        default = True,
                                        chronologyname = 'Default 210Pb')

uploader['datasetid'] = nu.insertDataset(cur, uploader['collunitid'], datasetname)

uploader['datasetpi'] = nu.insertDatasetPI(cur, uploader['datasetid'], piname[i], i + 1)

uploader['processor'] = nu.insertDatasetProcessor(cur, uploader['datasetid'])

uploader['repository'] = nu.insertDatasetRepository(cur, uploader['datasetid'])

nu.insertDatasetDatabase(cur, uploader['datasetid'], "")
nu.insertSamples(cur, ts.insertsample
ts.insertsampleanalyst
ts.insertsampleage
ts.insertdata

conn.commit()
conn.rollback()