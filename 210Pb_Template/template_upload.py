import json
import os
import psycopg2
import glob
from dotenv import load_dotenv
import neotomaUploader as nu

load_dotenv()

data = json.loads(os.getenv('PGDB_LOCAL'))

conn = psycopg2.connect(**data, connect_timeout = 5)
cur = conn.cursor()

args = nu.parse_arguments()

filenames = glob.glob(args['data'] + "*.csv")

for filename in filenames:
    print(filename)
    logfile = []
    hashcheck = nu.hash_file(filename)
    filecheck = nu.check_file(filename)

    if hashcheck['pass'] is False and filecheck['pass'] is False:
        csv_template = nu.read_csv(filename)
        logfile.append("File must be properly validated before it can be uploaded.")
    else:
        csv_template = nu.read_csv(filename)
        # This possibly needs to be fixed. How do we know that there is one or more header rows?

    uploader = {}

    yml_dict = nu.yml_to_dict(yml_file=args['yml'])
    yml_data = yml_dict['metadata']

    # Verify that the CSV columns and the YML keys match
    csv_valid = nu.csv_validator(filename = filename,
                                yml_data = yml_data)
    try:
        logfile.append('=== Inserting new Site ===')
        uploader['siteid'] = nu.insert_site(cur = cur,
                                        yml_dict = yml_dict,
                                        csv_template = csv_template)
        logfile.append(f"siteid: {uploader['siteid']}")

        # logfile.append('=== Inserting Site Geopol ===')
        # uploader['geopolid'] = nu.insert_geopol(cur = cur,
        #                                        yml_dict = yml_dict,
        #                                        csv_template = csv_template,
        #                                        uploader = uploader)
        # logfile.append(f"Geopolitical Unit: {uploader['geopolid']}")

        logfile.append('=== Inserting Collection Units ===')
        uploader['collunitid'] = nu.insert_collunit(cur = cur,
                                                yml_dict = yml_dict,
                                                csv_template = csv_template,
                                                uploader = uploader)
        logfile.append(f"collunitid: {uploader['collunitid']}")

logfile.append('=== Inserting Collection Units ===')
uploader['collunitid'] = nu.insert_collunit(cur = cur,
                                           yml_dict = yml_dict,
                                           csv_template = csv_template,
                                           uploader = uploader)

        logfile.append('=== Inserting Chroncontrol ===')
        uploader['chroncontrol'] = nu.insert_chron_control(cur = cur,
                                                        yml_dict = yml_dict,
                                                        csv_template = csv_template,
                                                        uploader = uploader)
        logfile.append(f"chroncontrol: {uploader['chroncontrol']}")

        logfile.append('=== Inserting Dataset ===')
        uploader['datasetid'] = nu.insert_dataset(cur = cur,
                                                yml_dict = yml_dict,
                                                csv_template = csv_template,
                                                uploader = uploader)
        logfile.append(f"datasetid: {uploader['datasetid']}")

        logfile.append('=== Inserting Dataset PI ===')
        uploader['datasetpi'] = nu.insert_dataset_pi(cur = cur,
                                                    yml_dict = yml_dict,
                                                    csv_template = csv_template,
                                                    uploader = uploader)
        logfile.append(f"datasetPI: {uploader['datasetpi']}")

        logfile.append('=== Inserting Data Processor ===')
        uploader['processor'] = nu.insert_data_processor(cur = cur,
                                                        yml_dict = yml_dict,
                                                        csv_template = csv_template,
                                                        uploader = uploader)
        logfile.append(f"dataset Processor: {uploader['processor']}")

        # Not sure where to get this information from
        # logfile.append('=== Inserting Repository ===')
        # uploader['repository'] = nu.insert_dataset_repository(cur = cur,
        #                                                     yml_dict = yml_dict,
        #                                                     csv_template = csv_template,
        #                                                     uploader = uploader)
        # logfile.append(f"dataset Processor: {uploader['repository']}")

        logfile.append('=== Inserting Dataset Database ===')
        uploader['database'] = nu.insert_dataset_database(cur = cur,
                                                        yml_dict = yml_dict,
                                                        uploader = uploader)
        logfile.append(f"Dataset Database: {uploader['database']}")

        logfile.append('=== Inserting Samples ===')
        uploader['samples'] = nu.insert_sample(cur, 
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)
        logfile.append(f"Dataset Samples: {uploader['samples']}")

        logfile.append('=== Inserting Sample Analyst ===')
        uploader['sampleAnalyst'] = nu.insert_sample_analyst(cur, 
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)
        logfile.append(f"Sample Analyst: {uploader['sampleAnalyst']}")

        logfile.append('=== Inserting Sample Age ===')
        uploader['sampleAge'] = nu.insert_sample_age(cur, 
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)
        logfile.append(f"Sample Age: {uploader['sampleAge']}")

        logfile.append('=== Inserting Data ===')
        uploader['data'] = nu.insert_data(cur, 
                                        yml_dict = yml_dict,
                                        csv_template = csv_template,
                                        uploader = uploader)
        logfile.append(f"Data: {uploader['data']}")

        with open(filename + '.upload.log', 'w', encoding = "utf-8") as writer:
                for i in logfile:
                    writer.write(i)
                    writer.write('\n')
                    
    except Exception as e:
         logfile.append(f"File: {filename} could not be uploaded. Review logs.")
         logfile.append(f"An exception occurred: {str(e)}")
         with open(filename + '.upload.log', 'w', encoding = "utf-8") as writer:
                for i in logfile:
                    writer.write(i)
                    writer.write('\n')
         

# conn.commit()
#print(logfile)
conn.rollback()