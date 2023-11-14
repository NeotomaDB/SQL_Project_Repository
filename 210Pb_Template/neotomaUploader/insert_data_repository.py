import logging
from .pull_params import pull_params
import numpy as np

def insert_data_repository(cur, yml_dict, csv_template, uploader):
    """
    """

    repo_query = """
                 SELECT ts.insertrepositoryinstitution(_acronym := %(acronym)s,
                                                       _repository := %(repository)s,
                                                       _notes := %(notes)s)
                 """    
    params = ['acronym', 'repo']
    inputs = pull_params(params, yml_dict, csv_template, 'ndb.repository')

    return