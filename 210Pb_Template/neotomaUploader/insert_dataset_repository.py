
import logging
from .pull_params import pull_params

def insert_dataset_repository(cur, yml_dict, csv_template, uploader):
    params = ['contactid']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.sampleanalysts')
    repo_query = """SELECT ts.insertdatasetrepository(_acronym:= %(acronym)s,
                                                          _repository := %(repository)s,
                                                          _notes := %(notes)s);"""
    #_datasetid integer, _repositoryid integer, _notes character varying DEFAULT NULL::character varying)

    
    return None