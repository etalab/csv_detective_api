'''Analyzes a folder of csv files with csv_detective. The column type detection is done with
  both the Rule Based (RB) and/or Machine Learning (ML) approaches.
  Saves the results as a JSON file.

Usage:
    analyze_csv_cli.py <i> [options]

Arguments:
    <i>                                An input directory with csvs(if dir it will convert all txt files inside).
    --analysis_type ANAL_TYPE          The type of column type analysis: rule, mlearning, both [default: "both":str]
    --num_files NFILES                 Number of files (CSVs) to work with [default: 10:int]
    --num_rows NROWS                   Number of rows per file to use [default: 200:int]
    --num_cores=<n> CORES                  Number of cores to use [default: 1:int]
'''
import json

import joblib
from argopt import argopt
from csv_detective.explore_csv import routine
from joblib import Parallel, delayed, load
from tqdm import tqdm

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

from prediction import get_columns_prediction, get_columns_types
from utils import extract_id, get_files
ML_PIPELINE = None


def analyze_csv(file_path, analysis_type="both", pipeline=None):
    dict_result = {}
    logger.info(" csv_detective on {}".format(file_path))

    if analysis_type == "both" or analysis_type == "rule":
        try:
            dict_result = routine(file_path, num_rows=100)
        except Exception as e:
            logger.debug("Analyzing file {0} failed with {1}".format(file_path, e))
            return extract_id(file_path), dict_result

        if "columns" in dict_result:
            dict_result["columns_rb"] = dict_result["columns"]
            dict_result.pop("columns")
    else:
        # Get ML tagging
        try:
            dict_result = routine(file_path, num_rows=100, user_input_tests=None)
        except Exception as e:
            logger.debug("Analyzing file {0} failed with {1}".format(file_path, e))
            return extract_id(file_path), dict_result

    if analysis_type != "rule":
        assert pipeline is not None
        y_pred, csv_info = get_columns_prediction(file_path, pipeline)
        dict_result["columns_ml"] = get_columns_types(y_pred, csv_info)

    return extract_id(file_path), dict_result


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    csv_folder_path = parser.i
    analysis_type = parser.analysis_type
    num_files = parser.num_files
    num_rows = parser.num_rows
    n_jobs = int(parser.num_cores)
    if analysis_type != "rule":
        logger.info("Loading ML model...")
        ML_PIPELINE = joblib.load('csv_detective_ml/models/model.joblib')

    # list_files = ["03c24270-75ac-4a06-9648-44b6b5a5e0f7.csv"]
    list_files = get_files(csv_folder_path)

    if n_jobs and n_jobs > 1:
        csv_info = Parallel(n_jobs=n_jobs)(
            delayed(analyze_csv)(file_path, analysis_type=analysis_type, pipeline=ML_PIPELINE)
            for file_path in tqdm(list_files))
    else:
        csv_info = [analyze_csv(f, analysis_type=analysis_type, pipeline=ML_PIPELINE)
                    for f in tqdm(list_files)]

    logger.info("Saving info to JSON")
    json.dump(dict(csv_info), open("./csv_data.json", "w"))
    pass




