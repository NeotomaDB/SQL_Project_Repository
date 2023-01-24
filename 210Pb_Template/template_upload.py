import sys
import json
import psycopg2
import datetime

from functions import read_csv, insertSite, insertCollUnit, cleanCol
from functions import assocGeopol, insertAnalysisUnit, insertChronology

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
ages = cleanCol('210Pb Date', template, False)
agemodel = cleanCol('210 Lead Model', template)
chronnotes = cleanCol('210 Lead Model Parameters', template)
agetype = cleanCol('210Pb Date Units', template)


logfile.append('=== Inserting new Site ===')
uploader['siteid'] = insertSite(conn = conn, sitename = sitename, coords = coords)
logfile.append('siteid: %s' % uploader['siteid'])

logfile.append('=== Inserting Site Geopol ===')
uploader['geopolid'] = assocGeopol(conn = conn, siteid = uploader['siteid'])
logfile.append('Geopolitical Unit: %s' % uploader['siteid'])

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = insertCollUnit(conn = conn, collunits = collunits, 
                                        colldate = colldate, siteid = uploader['siteid'],
                                        coords = coords, location = location)
logfile.append('collunitid: %s' % uploader['collunitid'])

logfile.append('=== Inserting Analysis Units ===')
dthick = []
for i in range(len(depths)):
    dthick.append({'depth': depths[i], 'thickness': thicks[i]})

uploader['anunits'] = insertAnalysisUnit(conn = conn,
                                         collunitid = uploader['collunitid'],
                                         dthick = dthick)

logfile.append('=== Inserting Chronology ===')
uploader['chronology'] = insertChronology(conn = conn, 
                                          collunitid = uploader['collunitid'],
                                          agetype = agetype[1], 
                                          agemodel = agemodel[0],
                                          ages = ages,
                                          contactname = modelername,
                                          default = True,
                                          chronologyname = 'Default 210Pb')
