import sys
import json
import psycopg2
import datetime

from functions import read_csv, validunits, insertSite, insertCollUnit, validAgent, validGeoPol, cleanCol
from functions import cleanCol

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = sys.argv

if len(args) > 1:
    filename = args[1]
else:
    filename = 'data/AgnesTemplateFixed.csv'

template = read_csv(filename)
del template[0]
del template[0]

logfile = []

uploader = {}

# Cleaning fields to unique values:
sitename = cleanCol('Site name', template)
coords = cleanCol('Geographic coordinates (lat, long)', template)
geog = cleanCol('Location (country, state/province, etc.)', template)
piname = cleanCol('Dataset PI', template)
analystname = cleanCol('Analyst (person/lab)', template)
modelername = cleanCol('Modeler (person/lab)', template)
pubname = cleanCol('Publications', template)
collunits = cleanCol('Core number or code', template)
colldate = cleanCol('Date of core collection', template)
location = cleanCol('Coordinate precision', template)
depths = cleanCol('Depth', template, False)
thicks = cleanCol('Thickness', template, False)
dateunits = cleanCol('210Pb Date Units', template)
ages = cleanCol('210Pb Date', template)

logfile.append('=== Inserting new Site ===')
uploader['siteid'] = insertSite(conn = conn, sitename = sitename, coords = coords)
logfile.append('siteid: %s' % uploader['siteid'])

logfile.append('=== Inserting Site Geopol ===')
uploader['geopolid'] = assocGeopol(conn = conn, siteid = uploader['siteid'])

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = insertCollUnit(conn = conn, collunits = collunits, 
                                        colldate = colldate, siteid = uploader['siteid'],
                                        coords = coords, location = location)
logfile.append('collunitid: %s' % uploader['collunitid'])

logfile.append('=== Inserting Analysis Units ===')
dthick = []
for i in range(0,20):
    dthick.append({'depth': depths[i], 'thickness': thicks[i]})
uploader['anunits'] = insertAnalysisUnit(conn = conn, collunitid = uploader['collunitid'], dthick = dthick)

logfile.append('=== Inserting Chronology ===')



# Testing geopolitical unit:
logfile.append('=== Checking Against Geopolitical Units ===')
namecheck = validGeoPol(cur, geog, coords)
if namecheck['pass'] is False:
    logfile.append(f"Your written location does not match cleanly. Coordinates suggest \'{namecheck['placename']}\'")
else:
    testset['geopol'] = True

# Testing PI names:
logfile.append('=== Checking Against Dataset PI Name ===')
namecheck = validAgent(cur, piname)
if namecheck['pass'] is False:
    if namecheck['name'] is None:
        logfile.append(f"The PI name must be a single repeated name.")
    else:
        logfile.append(f"There is no exact name match in the database. Please either enter a new name or select:")
        for i in namecheck['name']:
            logfile.append(f"Close name match \'{i}\'")
else:
    testset['piname'] = True

# Testing 
logfile.append('=== Checking Against Age Modeller Name(s) ===')
namecheck = validAgent(cur, modelername)
if namecheck['pass'] is False:
    if namecheck['name'] is None:
        logfile.append(f"The Age Modeller name must be a single repeated name.")
    else:
        logfile.append(f"There is no exact name match in the database. Please either enter a new name or select:")
        for i in namecheck['name']:
            logfile.append(f"Close name match \'{i}\'")
else:
    testset['modellername'] = True

logfile.append('=== Checking Against Analyst Name(s) ===')
allnames = []
for i in analystname:
    logfile.append(f"*** Analyst: {i} ***")
    namecheck = validAgent(cur, [i])
    if namecheck['pass'] is False:
        allnames.append(False)
        if namecheck['name'] is None:
            logfile.append(f"The Age Modeller name must be a single repeated name.")
        else:
            logfile.append(f"There is no exact name match in the database. Please either enter a new name or select:")
            for i in namecheck['name']:
                logfile.append(f"Close name match \'{i}\'")
    else:
        allnames.append(True)

if all(allnames) is True:
    testset['modellername'] = True

with open('template.log', 'a') as writer:
    for i in logfile:
        writer.write(i)
        writer.write('\n')
