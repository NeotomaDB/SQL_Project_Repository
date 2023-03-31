import sys
import json
import psycopg2
import datetime

from functions import read_csv, insertSite, insertCollUnit, cleanCol
from functions import assocGeopol, insertAnalysisUnit, insertChronology
from functions import insertChronControl

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = sys.argv

if len(args) > 1:
    filename = args[1]
else:
    filename = 'data/Speckled Trout 2006 GRPO.csv'

template = read_csv(filename)
del template[0]
del template[0]

logfile = []

uploader = {}

# Cleaning fields to unique values:
sitename = cleanCol('Site.name', template)
coords = cleanCol('Geographic.coordinates', template)
geog = cleanCol('Location', template)
piname = cleanCol('Principal.Investigator.s.', template)
analystname = cleanCol('Analyst', template)
modelername = cleanCol('Modeler', template)
pubname = cleanCol('Publications', template)
collunits = cleanCol('Core.number.or.code', template)
colldate = cleanCol('Date.of.core.collection', template)
location = cleanCol('Coordinate.precision', template)
depths = cleanCol('Depth', template, False)
thicks = cleanCol('Thickness', template, False)
dateunits = cleanCol('X210Pb.Date.Units', template)
ages = cleanCol('X210Pb.Date', template, False)
ageerror = cleanCol('Error..210Pb.Date.', template, False)
agemodel = cleanCol('X210.LeadModel', template)
chronnotes = cleanCol('X210.Lead.Model.Notes', template)
datasetname = cleanCol('Core.number.or.code', template)

dthick = []
for i in range(len(depths)):
    dthick.append({'depth': depths[i], 'thickness': thicks[i], 'age': ages[i], 'error': ageerror[i]})

logfile.append('=== Inserting new Site ===')
uploader['siteid'] = insertSite(cur = cur, sitename = sitename, coords = coords)
logfile.append('siteid: %s' % uploader['siteid'])

logfile.append('=== Inserting Site Geopol ===')
uploader['geopolid'] = assocGeopol(cur = cur, siteid = uploader['siteid'])
logfile.append('Geopolitical Unit: %s' % uploader['geopolid'])

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = insertCollUnit(cur = cur, collunits = collunits, 
                                        colldate = colldate, siteid = uploader['siteid'],
                                        coords = coords, location = location)
logfile.append('collunitid: %s' % uploader['collunitid'])

logfile.append('=== Inserting Analysis Units ===')
dthick = []
for i in range(len(depths)):
    dthick.append({'depth': depths[i], 'thickness': thicks[i]})

uploader['anunits'] = insertAnalysisUnit(cur = cur,
                                         collunitid = uploader['collunitid'],
                                         dthick = dthick)

logfile.append('=== Inserting Chronology ===')
uploader['chronology'] = insertChronology(cur = cur, 
                                          collunitid = uploader['collunitid'],
                                          agetype = agetype[1], 
                                          agemodel = agemodel[0],
                                          ages = ages,
                                          contactname = modelername,
                                          default = True,
                                          chronologyname = 'Default 210Pb')

logfile.append('=== Inserting Chroncontrol ===')
uploader['chroncontrol'] = insertChrocontrol(cur = cur, 
                                          collunitid = uploader['collunitid'],
                                          agetype = agetype[1], 
                                          agemodel = agemodel[0],
                                          ages = ages,
                                          contactname = modelername,
                                          default = True,
                                          chronologyname = 'Default 210Pb')

uploader['datasetid'] = insertDataset(cur, uploader['collunitid'], datasetname)

uploader['datasetpi'] = insertDatasetPI(cur, uploader['datasetid'], piname[i], i + 1)

uploader['processor'] = insertDatasetProcessor(cur, uploader['datasetid'])

uploader['repository'] = insertDatasetRepository(cur, uploader['datasetid'])

insertDatasetDatabase(cur, uploader['datasetid'], "")
insertSamples(cur, ts.insertsample
ts.insertsampleanalyst
ts.insertsampleage
ts.insertdata
