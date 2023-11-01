import json
import os
import psycopg2
import glob
from dotenv import load_dotenv
import neotomaUploader as nu

load_dotenv()

data = json.loads(os.getenv('PGDB_LOCAL2'))

conn = psycopg2.connect(**data, connect_timeout = 5)

cur = conn.cursor()

args = nu.parse_arguments()

filenames = glob.glob(args['data'] + "*.csv")

for filename in filenames:
    test_dict = {}
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
        test_dict['site'] = True
    except Exception as e:
        test_dict['site'] = False
        test_dict['site_error'] = e 

    
        # logfile.append('=== Inserting Site Geopol ===')
        # uploader['geopolid'] = nu.insert_geopol(cur = cur,
        #                                        yml_dict = yml_dict,
        #                                        csv_template = csv_template,
        #                                        uploader = uploader)
        # logfile.append(f"Geopolitical Unit: {uploader['geopolid']}")

    try:
        logfile.append('=== Inserting Collection Units ===')
        uploader['collunitid'] = nu.insert_collunit(cur = cur,
                                                yml_dict = yml_dict,
                                                csv_template = csv_template,
                                                uploader = uploader)
        logfile.append(f"collunitid: {uploader['collunitid']}")
        test_dict['collunit'] = True
    except Exception as e:
        test_dict['collunit'] = False
        test_dict['collunit_error'] = e 

    try:
        logfile.append('=== Inserting Analysis Units ===')
        uploader['anunits'] = nu.insert_analysisunit(cur = cur,
                                                    yml_dict = yml_dict,
                                                    csv_template = csv_template,
                                                    uploader = uploader)
        logfile.append(f"anunits: {uploader['anunits']}")
        test_dict['anunits'] = True
    except Exception as e:
        test_dict['anunits'] = False
        test_dict['aunits_error'] = e 

    try:
        logfile.append('=== Inserting Chronology ===')
        uploader['chronology'] = nu.insert_chronology(cur = cur,
                                                    yml_dict = yml_dict,
                                                    csv_template = csv_template,
                                                    uploader = uploader)
        logfile.append(f"chronology: {uploader['chronology']}")
        test_dict['chronology'] = True
    except Exception as e:
        test_dict['chronology'] = False
        test_dict['chronology_error'] = e 

    try:
        logfile.append('=== Inserting Chroncontrol ===')
        uploader['chroncontrol'] = nu.insert_chron_control(cur = cur,
                                                        yml_dict = yml_dict,
                                                        csv_template = csv_template,
                                                        uploader = uploader)
        logfile.append(f"chroncontrol: {uploader['chroncontrol']}")
        test_dict['chroncontrol'] = True
    except Exception as e:
        test_dict['chroncontrol'] = False
        test_dict['chroncontrol_error'] = e

    try:
        logfile.append('=== Inserting Dataset ===')
        uploader['datasetid'] = nu.insert_dataset(cur = cur,
                                                yml_dict = yml_dict,
                                                csv_template = csv_template,
                                                uploader = uploader)
        logfile.append(f"datasetid: {uploader['datasetid']}")
        test_dict['dataset'] = True
    except Exception as e:
        test_dict['dataset'] = False
        test_dict['dataset_error'] = e

    try:
        logfile.append('=== Inserting Dataset PI ===')
        uploader['datasetpi'] = nu.insert_dataset_pi(cur = cur,
                                                    yml_dict = yml_dict,
                                                    csv_template = csv_template,
                                                    uploader = uploader)
        logfile.append(f"datasetPI: {uploader['datasetpi']}")
        test_dict['datasetpi'] = True
    except Exception as e:
        test_dict['datasetpi'] = False
        test_dict['datasetpi_error'] = e

    try:
        logfile.append('=== Inserting Data Processor ===')
        uploader['processor'] = nu.insert_data_processor(cur = cur,
                                                        yml_dict = yml_dict,
                                                        csv_template = csv_template,
                                                        uploader = uploader)
        logfile.append(f"dataset Processor: {uploader['processor']}")
        test_dict['processor'] = True
    except Exception as e:
        test_dict['processor'] = False
        test_dict['processor_error'] = e

        # Not sure where to get this information from
        # logfile.append('=== Inserting Repository ===')
        # uploader['repository'] = nu.insert_dataset_repository(cur = cur,
        #                                                     yml_dict = yml_dict,
        #                                                     csv_template = csv_template,
        #                                                     uploader = uploader)
        # logfile.append(f"dataset Processor: {uploader['repository']}")

    try:
        logfile.append('=== Inserting Dataset Database ===')
        uploader['database'] = nu.insert_dataset_database(cur = cur,
                                                        yml_dict = yml_dict,
                                                        uploader = uploader)
        logfile.append(f"Dataset Database: {uploader['database']}")
        test_dict['database'] = True
    except Exception as e:
        test_dict['database'] = False
        test_dict['database_error'] = e


    try:
        logfile.append('=== Inserting Samples ===')
        uploader['samples'] = nu.insert_sample(cur, 
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)
        logfile.append(f"Dataset Samples: {uploader['samples']}")
        #print(uploader['samples'])
        test_dict['samples'] = True
    except Exception as e:
        test_dict['samples'] = False
        test_dict['samples_error'] = e

    try:
        logfile.append('=== Inserting Sample Analyst ===')
        uploader['sampleAnalyst'] = nu.insert_sample_analyst(cur, 
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)
        logfile.append(f"Sample Analyst: {uploader['sampleAnalyst']}")
        test_dict['sampleAnalyst'] = True
    except Exception as e:
        test_dict['sampleAnalyst'] = False
        test_dict['sampleAnalyst_error'] = e 

    try:
        logfile.append('=== Inserting Sample Age ===')
        uploader['sampleAge'] = nu.insert_sample_age(cur, 
                                            yml_dict = yml_dict,
                                            csv_template = csv_template,
                                            uploader = uploader)
        logfile.append(f"Sample Age: {uploader['sampleAge']}")
        test_dict['sampleAge'] = True
    except Exception as e:
        test_dict['sampleAge'] = False
        test_dict['sampleAge_error'] = e        

    try:
        logfile.append('=== Inserting Data ===')
        uploader['data'] = nu.insert_data(cur, 
                                        yml_dict = yml_dict,
                                        csv_template = csv_template,
                                        uploader = uploader)
        logfile.append(f"Data: {uploader['data']}")
        test_dict['data'] = True
    except Exception as e:
        test_dict['data'] = False
        test_dict['data_error'] = e

    with open(filename + '.upload.log', 'w', encoding = "utf-8") as writer:
                for i in logfile:
                    writer.write(i)
                    writer.write('\n')
    
    #print(filename, test_dict)
    all_true = all(value for value in test_dict.values())

    if all_true:
        print(filename, "upload")
        #conn.commit()
        #print(logfile)
        conn.rollback()
    else:
        print(f"filename {filename} could not be uploaded")
        print(test_dict)
        conn.rollback()
         
