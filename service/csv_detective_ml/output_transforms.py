'''

Usage:
    output_transforms.py <i> [options]

Arguments:
    <i>                                Input JSON analysis from analyze_csv_cli.py
    --cores=<n> CORES              Number of cores to use [default: 1:int]
'''

import json
import logging
from collections import defaultdict

from argopt import argopt
from joblib import Parallel, delayed
from tqdm import tqdm

logger = logging.getLogger('output_transforms')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(f'./logs/output_transforms.log', mode='w')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(funcName)s:\t%(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_columns_detected_by_resource(results_dict, analysis_type="columns_ml"):
    """
    Get the csv_Detective analysis dict and returns a new dict with exclusively the detected columns and the count
    of unique detected columns
    :param results_dict:
    :param analysis_type: Either columns_rb or columns_ml, for rule-based or machine learning analysis, respectively
    :return:
    """

    types_by_resource = defaultdict(dict)
    for resource_id, csv_data in results_dict.items():
        detected_columns = csv_data.get(analysis_type, None)
        if not detected_columns:
            continue
        detected_types = set()
        types_by_resource[resource_id]["detected_types"] = detected_columns
        for type_ in detected_columns.values():
            detected_types.update([type_[0]])
        types_by_resource[resource_id]["nb_unique_types"] = len(detected_types)

    types_by_resource = sorted(types_by_resource.items(), key=lambda x: x[1]["nb_unique_types"], reverse=True)

    return types_by_resource

def run():
    pass


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    csv_detective_result = parser.i
    n_jobs = parser.cores

    with open(csv_detective_result) as result:
        results_dict = json.load(result)

    types_by_resource = get_columns_detected_by_resource(results_dict)

    things_to_analyze = []

    if n_jobs < 2:
        job_output = []
        for stuff in tqdm(things_to_analyze):
            job_output.append(run(stuff))
    else:
        job_output = Parallel(n_jobs=n_jobs)(
            delayed(run)(stuff) for stuff in tqdm(things_to_analyze))
