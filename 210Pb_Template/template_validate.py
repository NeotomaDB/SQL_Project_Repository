import glob
import sys
import json
import psycopg2

from functions import read_csv, cleanCol
from validators import validunits, newSite, validAgent, validGeoPol, validCollUnit

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = sys.argv

if len(args) > 1:
    filename = glob.glob(args[1] + "*.csv")
else:
    filenames = glob.glob("data/" + "*.csv")

for filename in filenames:
    print(filename)
    template = read_csv(filename)

    logfile = []
    testset = {'units': False,
            'sites': False,
            'geopol': False,
            'piname': False,
            'analystname': False,
            'modelername': False}

    # Cleaning fields to unique values:
    sitename = cleanCol('Site.name', template)
    coords = cleanCol('Geographic.coordinates', template)
    geog = cleanCol('Location', template)
    piname = cleanCol('Principal.Investigator.s.', template)
    analystname = cleanCol('Analyst', template)
    modelername = cleanCol('Modeler', template)
    pubname = cleanCol('Publications', template)
    collunits = cleanCol('Core.number.or.code', template)

    unitcols = {'ddunits' : ['Dry.Density.Units'],
                'cdmunits' : ['Cumulative.dry.mass.units'],
                'riunits' : ['Total.210Pb.Alpha..synonym.Total.210Po..Units',
                             'Error..total.210Pb.alpha..units',
                             'Total.210Pb.Gamma.Units',
                             'Error..total.210Pb.Gamma..Units', 'X214Pb.Units',
                             'Error..214Pb..Units', 'X214Bi.Units',
                             'Error..214Bi..Units', 'X137Cs.Units',
                             'Error..137Cs..Units', 'Supported.210Pb.Units', 'Error..Supported.210Pb..1SD.Units', 
                             'Unsupported.210Pb.Units','Error..Unsupported.210Pb..1SD.Units'],
                'accum' : ['DMAR.Units', 'Error..DMAR..Units'],
                'timeunits' : ['Assigned.137Cs.Date.Units', 'X210Pb.Date.Units', 'Error..210Pb.Date..1SD.Units'],
                'precision' : ['Coordinate.precision'],
                'model': ['X210.LeadModel'],
                'estimate': ['Method.for.estimating.supported.210Pb'],
                'position': ['Depth.position']}

    units = {'ddunits': ['g/cm3'],
            'cdmunits': ['g/cm2'],
            'riunits': ['pCi/g', 'Bq/g', 'Bq/kg', 'dpm/g'],
            'accum': ['g/cm2/yr','g/m2/yr','kg/m2/yr'],
            'timeunits': ['CE/BCE', 'cal yr BP', 'Cal yr BP'],
            'precision': ['core-site','GPS','core-site approximate','lake center'],
            'model': ['CRS', 'CIC', 'CF:CS', 'PLUM', 'other'],
            'estimate': ['asymptote of alpha', 'gamma point-subtraction', 'gamma average'],
            'position': ['Top', 'Mid', 'Bottom']}

    logfile.append(f"Printing report for {filename}")

    # Testing Data Units:
    unittest = validunits(template, unitcols, units)
    logfile.append('=== Checking Template Unit Definitions ===')
    if len(unittest) > 0:
        for i in unittest:
            logfile.append('Invalid units within the template column \'%s\'' % i)
    else:
        logfile.append('No unit mismatch found.')
        testset['units'] = True

    # Testing site coordinates:
    logfile.append('=== Checking Against Current Sites ===')
    sitecheck = newSite(cur, coords)
    if sitecheck['pass'] is False and len(sitecheck['sitelist']) > 0:
        logfile.append('Multiple sites exist close to the requested site.')
        for i in sitecheck['sitelist']:
            logfile.append(f"siteid: {i['id']};  sitename: {i['name']:<25}; distance (m): {i['distance (m)']:<7} coords: [{i['coordlo']}, {i['coordlo']}]")
    else:
        testset['sites'] = True

    ########### Collection Units
    logfile.append('=== Checking Against Collection Units ===')
    nameCheck = validCollUnit(cur, coords, collunits)

    if testset['sites'] is True and nameCheck['pass'] is False:
        # We've got an existing site but the collunit does not exist at the site:
        logfile.append('The site exists, but no collection unit with this name exists.')
        logfile.append(f"Existing collection units for this site are: {nameCheck['collunits']}")
    if nameCheck['pass'] is False and len(nameCheck['collunits']) == 0:
        if len(coords) > 1:
            logfile.append('There is more than one set of coordinates associated with this site.')
        else:
            logfile.append('There are no coordinates associated with this file.')


    ########### Geopolitical unit:
    logfile.append('=== Checking Against Geopolitical Units ===')
    namecheck = validGeoPol(cur, geog, coords)
    if namecheck['pass'] is False and len(namecheck) > 0:
        logfile.append(f"Your written location does not match cleanly. Coordinates suggest \'{namecheck['placename']}\'")
    elif namecheck['pass'] is False and len(namecheck) == 0:
        logfile.append(f"Your written location does not match cleanly. No coordinates were provided.")
    else:
        testset['geopol'] = True

    ########### PI names:
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

    ########### Age Modeller Name
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

    ########### Analyst Name
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

    with open(filename + '.log', 'a') as writer:
        for i in logfile:
            writer.write(i)
            writer.write('\n')
