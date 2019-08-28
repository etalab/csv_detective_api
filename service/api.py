#!flask/bin/python
import os
import sys
sys.path.append("./csv_detective_ml")  # horrible hack to load my features class to load my ML pipeline :/
from flask import Flask
from flask import request
from flask import jsonify
from flask_restplus import Api, Resource, fields
from flask_cors import CORS
from tempfile import NamedTemporaryFile

import logging
import json

import features  # needed to load ML PIPELINE
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


model = api.model('Analysis parameters',
                  {'resource_id': fields.String(required=True,
                                                description="DGF Resource ID or CSV path",
                                                help="Resource ID cannot be blank")
                   }
                  # 'textField2': fields.String(required=True,
                  #                             description="Text Field 2",
                  #                             help="Text Field 2 cannot be blank"),

                  )
CSV_INFO = {}
ML_PIPELINE = None

def load_ml_model():
    global ML_PIPELINE
    logger.info("Loading ML model...")
    ML_PIPELINE = load('./csv_detective_ml/models/model.joblib')
    return ML_PIPELINE

load_ml_model()

@ns_csv_detective.route("/")
class CSVDetectiveAPI(Resource):
    @api.expect(model)
    def get(self):
        global CSV_INFO
        try:
            resource_id = request.args.get('resource_id')
            if resource_id in CSV_INFO:
                response = CSV_INFO[resource_id]
                response = reformat_response(response)
                response = link_reference_datasets(response)
                return jsonify(response)
            else:
                logger.info("Resource id not found in 'database'.")
                return jsonify({"error": "ID {} not found".format(resource_id)})
        except Exception as e:
            return jsonify({"error": str(e)})
        # return {'hello': 'world'}

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

@ns_csv_detective.route("/isAlive")
class IsAlive(Resource):
    def get(self):
        return "True"


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


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


if __name__ == '__main__':
    # load csv_detective info json
    try:
        with open("./data/csv_data.json", "r") as filo:
            logger.info("Loading JSON file with csv info...")
            CSV_INFO = json.load(filo)

    except Exception as e:
        logger.error("Error reading JSON data file: {0}".format(str(e)))
        exit(1)

    if 'ENVIRONMENT' in os.environ:
        if os.environ['ENVIRONMENT'] == 'production':
            app.run(port=80, host='0.0.0.0')
        if os.environ['ENVIRONMENT'] == 'local':
            app.run(port=5000, host='0.0.0.0')
    else:
        app.run(port=5000, host='0.0.0.0')
