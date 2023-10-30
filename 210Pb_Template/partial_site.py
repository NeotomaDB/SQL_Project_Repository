import json
import os
import psycopg2
from dotenv import load_dotenv
import neotomaUploader as nu

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

yml_dict = nu.yml_to_dict(yml_file=args['yml'])
yml_data = yml_dict['metadata']

# Verify that the CSV columns and the YML keys match
csv_valid = nu.csv_validator(filename = FILENAME,
                            yml_data = yml_data)

logfile.append('=== Inserting new Site ===')
uploader['siteid'] = nu.insert_site(cur = cur,
                                   yml_dict = yml_dict,
                                   csv_template = csv_template)

logfile.append(f"siteid: {uploader['siteid']}")

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = nu.insert_collunit(cur = cur,
                                           yml_dict = yml_dict,
                                           csv_template = csv_template,
                                           uploader = uploader)

logfile.append(f"collunitid: {uploader['collunitid']}")
print(logfile)

