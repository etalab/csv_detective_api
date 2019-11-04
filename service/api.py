#!flask/bin/python
import os
import sys
from collections import defaultdict

sys.path.append("./csv_detective_ml")  # horrible hack to load my features class to load my ML pipeline :/
from flask import Flask
from flask import request
from flask import jsonify
from flask_restplus import Api, Resource, fields
from flask_cors import CORS
from tempfile import NamedTemporaryFile

import logging
import json

from joblib import load
from utils.reference_matcher import link_reference_datasets
from utils.parsers import file_upload

from csv_detective_ml.analyze_csv_cli import analyze_csv

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
CORS(app)

api = Api(app=app,
          version="0.1",
          title="CSV Detective API",
          description="Get info about the data contained in a DGF CSV file.")

ns_csv_detective = api.namespace('csv_detective', description='Get data from DGF CSVs')

resource_model = api.model('Analysis parameters',
                           {'resource_id': fields.String(required=True,
                                                         description="DGF Resource ID or CSV path",
                                                         help="Resource ID cannot be blank")
                            })

type_model = api.model('Type analysis parameters',
                       {'target_type': fields.String(required=True,
                                                     description="Target type to find among resources/datasets",
                                                     help="Resource ID cannot be blank")
                        })

DATASET_CSV_INFO = {}
TYPE_CSV_INFO = defaultdict(lambda: defaultdict(dict))
ML_PIPELINE = None


def load_ml_model():
    global ML_PIPELINE
    logger.info("Loading ML model...")
    ML_PIPELINE = load('./csv_detective_ml/models/model.joblib')
    return ML_PIPELINE


load_ml_model()


@ns_csv_detective.route("/dataset_id")
class CSVDetectiveDataset(Resource):
    @api.expect(resource_model)
    def get(self):
        global DATASET_CSV_INFO
        try:
            resource_id = request.args.get('resource_id')
            if resource_id in DATASET_CSV_INFO:
                response = DATASET_CSV_INFO[resource_id]
                response = reformat_response(response)
                response = link_reference_datasets(response)
                return jsonify(response)
            else:
                logger.info("Resource id not found in 'database'.")
                return jsonify({"error": "ID {} not found".format(resource_id)})
        except Exception as e:
            return jsonify({"error": str(e)})


@ns_csv_detective.route("/resource_id")
class CSVDetectiveResource(Resource):
    @api.expect(resource_model)
    def get(self):
        global DATASET_CSV_INFO
        try:
            resource_id = request.args.get('resource_id')
            if resource_id in DATASET_CSV_INFO:
                response = DATASET_CSV_INFO[resource_id]
                response = reformat_response(response)
                response = link_reference_datasets(response)
                return jsonify(response)
            else:
                logger.info("Resource id not found in 'database'.")
                return jsonify({"error": "ID {} not found".format(resource_id)})
        except Exception as e:
            return jsonify({"error": str(e)})

    @ns_csv_detective.expect(file_upload)
    def post(self):

        args = file_upload.parse_args()
        if "resource_csv" in args and args["resource_csv"].mimetype != "text/csv":
            return jsonify({"error": "No uploaded file or the file seems to not be a CSV."})

        if ML_PIPELINE is None:
            analysis_type = "rule"
        else:
            analysis_type = "both"
        uploaded_csv = args["resource_csv"]

        tmp = NamedTemporaryFile(delete=False)

        try:
            tmp.write(uploaded_csv.read())
            tmp.close()
            _, response = analyze_csv(tmp.name, analysis_type=analysis_type, pipeline=ML_PIPELINE, num_rows=500)

        finally:
            os.remove(tmp.name)

        response = reformat_response(response)
        response = link_reference_datasets(response)
        return jsonify(response)


@ns_csv_detective.route("/type")
class CSVDetectiveType(Resource):
    @api.expect(type_model)
    def get(self):
        global TYPE_CSV_INFO
        try:
            target_type = request.args.get('target_type')
            if target_type in TYPE_CSV_INFO:
                response = TYPE_CSV_INFO[target_type]
                return jsonify(response)
            else:
                logger.info("Type not found in 'database'.")
                return jsonify({"error": "Type {} not found".format(target_type)})
        except Exception as e:
            return jsonify({"error": str(e)})


@ns_csv_detective.route("/isAlive")
class IsAlive(Resource):
    def get(self):
        return "True"


def reformat_response(response):
    response = dict(response)
    new_response = {}
    if "columns_rb" in response:
        reformatted_rb = {k: v[0] for k, v in response["columns_rb"].items()}
        new_response["columns_rb"] = reformatted_rb
        response.pop("columns_rb")
    if "columns_ml" in response:
        reformatted_ml = {k: v[0] for k, v in response["columns_ml"].items()}
        new_response["columns_ml"] = reformatted_ml
        response.pop("columns_ml")

    new_response["metadata"] = dict(response)
    return new_response


def load_result_dict():
    global DATASET_CSV_INFO
    try:
        with open("./data/interim/2019-10-25-11_59_dgf_friendly.json", "r") as filo:
            logger.info("Loading JSON file with csv info...")
            DATASET_CSV_INFO = json.load(filo)

    except Exception as e:
        logger.error("Error reading JSON data file: {0}".format(str(e)))
        exit(1)

    return DATASET_CSV_INFO


def crate_type_index(dataset_csv_info):
    """
    Invert the results dict to have a mapping of types --> dataset (and resource). Something like this:
    {
        type1: {
                    datasetID1: { resourceID1 : {csv_detective results}, {...} }
    }
    :return:
    """
    results_keynames = ["columns_rb", "columns_ml"]

    def extract_types_detected(csv_detective_results):

        detected_types = set([])
        for res in results_keynames:
            if res not in csv_detective_results:
                continue
            detected_types.update([f[0] for f in csv_detective_results[res].values()])
        return detected_types

    for dataset_id, resources in dataset_csv_info.items():
        for resource_id, csv_detective_result in resources.items():
            if not any([f in csv_detective_result for f in results_keynames]):
                continue
            for type_detected in extract_types_detected(csv_detective_result):
                TYPE_CSV_INFO[type_detected][dataset_id][resource_id] = csv_detective_result

    return TYPE_CSV_INFO


if __name__ == '__main__':
    # load csv_detective info json
    DATASET_CSV_INFO = load_result_dict()
    TYPE_CSV_INFO = crate_type_index(DATASET_CSV_INFO)
    if 'ENVIRONMENT' in os.environ:
        if os.environ['ENVIRONMENT'] == 'production':
            app.run(port=80, host='0.0.0.0')
        if os.environ['ENVIRONMENT'] == 'local':
            app.run(port=5000, host='0.0.0.0')
    else:
        app.run(port=5000, host='0.0.0.0')
