#!flask/bin/python
import os

from flask import Flask
from flask import request
from flask import jsonify

from flask_restplus import Api, Resource, fields

import logging
import json
from utils.reference_matcher import link_reference_datasets
from utils.parsers import file_upload

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
api = Api(app=app,
          version="0.1",
          title="DGF Column Linker",
          description="Get the types contained in a DGF CSV file and link them to their respective reference dataset.")

ns_csv_linker = api.namespace('csv_linker', description='Link CSVs')

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


@ns_csv_linker.route("/")
class CSVLinker(Resource):
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

    @ns_csv_linker.expect(file_upload)
    def post(self):
        args = file_upload.parse_args()
        if args["resource_csv"].mimetype != "text/csv":
            return jsonify({"error": "The uploaded file seems to not be a CSV."})

        pass


@ns_csv_linker.route("/isAlive")
class IsAlive(Resource):
    def get(self):
        return "True"


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', "Content-Type")
    response.headers.add('Access-Control-Allow-Methods', "*")
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
        with open("csv_data.json", "r") as filo:
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
