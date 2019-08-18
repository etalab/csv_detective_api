#!flask/bin/python
import os

from flask import Flask
from flask import make_response
from flask import request
from flask import jsonify

from flask_restplus import Api, Resource, fields

import logging
import json

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
                  {'textField1': fields.String(required=True,
                                               description="DGF Resource ID or CSV path",
                                               help="Text Field 1 cannot be blank")
                   }
                  # 'textField2': fields.String(required=True,
                  #                             description="Text Field 2",
                  #                             help="Text Field 2 cannot be blank"),
                  # 'select1': fields.Integer(required=True,
                  #                           description="Select 1",
                  #                           help="Select 1 cannot be blank"),
                  # 'select2': fields.Integer(required=True,
                  #                           description="Select 2",
                  #                           help="Select 2 cannot be blank"),
                  # 'select3': fields.Integer(required=True,
                  #                           description="Select 3",
                  #                           help="Select 3 cannot be blank")}
                  )


@ns_csv_linker.route("/")
class CSVLinker(Resource):
    # def options(self):
    #     response = make_response()
    #     response.headers.add("Access-Control-Allow-Origin", "*")
    #     response.headers.add('Access-Control-Allow-Headers', "Content-Type")
    #     response.headers.add('Access-Control-Allow-Methods', "*")
    #     return response

    # @cors.crossdomain(origin='*')
    @api.expect(model)
    def get(self):
        global CSV_INFO
        try:
            resource_id = request.args.get('resource_id')
            if resource_id in CSV_INFO:
                return jsonify(CSV_INFO[resource_id])
            else:
                logger.info("Resource id not found in 'database'.")
                return jsonify({"error": "ID {} not found".format(resource_id)})
        except Exception as e:
            return jsonify({"error": str(e)})
        # return {'hello': 'world'}


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


CSV_INFO = {}


#
# @app.route('/csv_detective', methods=['GET'])
# def get_prediction():
#     global CSV_INFO
#     try:
#         resource_id = request.args.get('resource_id')
#         if resource_id in CSV_INFO:
#             return jsonify(CSV_INFO[resource_id])
#         else:
#             logger.info("Resource id not found in 'database'.")
#             return jsonify({"error": "ID {} not found".format(resource_id)})
#     except Exception as e:
#         return jsonify({"error": str(e)})
#
#
# @app.route('/dgf_column_linker', methods=['GET'])
# def dgf_column_linker():
#     try:
#         resource_id = request.args.get('resource_id')
#         if resource_id in CSV_INFO:
#             info_reformatted = {k: v for k, v in CSV_INFO[resource_id] if k not in ["columns_rb", "columns_ml"]}
#             info_reformatted["metadata"] = info_reformatted
#             for detection_type in ["columns_rb", "columns_ml"]:
#                 if detection_type in CSV_INFO[resource_id]:
#                     info_reformatted[detection_type] = CSV_INFO[resource_id][detection_type]
#
#             return jsonify(info_reformatted)
#
#         else:
#             logger.info("Resource id not found in 'database'.")
#             return jsonify({"error": "ID {} not found".format(resource_id)})
#     except Exception as e:
#         return jsonify({"error": str(e)})
#

def reformat_response(response):
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
